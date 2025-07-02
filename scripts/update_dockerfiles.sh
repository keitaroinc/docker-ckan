#!/bin/bash
set -e

echo "Starting Dockerfile package updates..."

# Base image to check against
BASE_IMAGE="python:3.10.18-alpine"

# Get the Alpine version from the base image
echo "Checking Alpine version in base image..."
ALPINE_VERSION=$(docker run --rm "$BASE_IMAGE" cat /etc/alpine-release)
echo "   Alpine version: $ALPINE_VERSION"

# Function to get latest package version
get_package_version() {
    local package_name="$1"
    
    echo "Checking latest version for $package_name..." >&2
    local version=$(docker run --rm "$BASE_IMAGE" sh -c "
        apk update > /dev/null 2>&1
        apk info $package_name 2>/dev/null | head -1 | sed 's/.*-\([0-9][^[:space:]]*\) .*/\1/'
    " 2>/dev/null || echo "")
    
    if [ ! -z "$version" ]; then
        echo "   Latest $package_name: $version" >&2
        echo "$version"
    else
        echo "   Package $package_name not found in Alpine" >&2
        return 1
    fi
}

# List of Dockerfiles to check
DOCKERFILES=("images/ckan/2.10/Dockerfile" "images/ckan/2.11/Dockerfile")

# Extract packages from apk add blocks across all Dockerfiles
echo "Detecting packages from apk add blocks..."
all_packages=""
for dockerfile in "${DOCKERFILES[@]}"; do
    if [ -f "$dockerfile" ]; then
        echo "Scanning $dockerfile..."
        # Extract packages from multi-line apk add blocks
        dockerfile_packages=$(sed -n '/^RUN apk add/,/^$/{/^[[:space:]]*[a-z].*=/s/^[[:space:]]*\([a-z][a-z0-9-]*\)=.*/\1/p}' "$dockerfile" | sort | uniq)
        all_packages="$all_packages $dockerfile_packages"
    fi
done

# Get unique packages across all files
unique_packages=$(echo $all_packages | tr ' ' '\n' | sort | uniq | grep -v '^$' | tr '\n' ' ')
echo "Found packages: $unique_packages"

# Get latest versions for all detected packages
echo "Fetching latest versions for detected packages..."
declare -A package_versions
for pkg in $unique_packages; do
    if [ ! -z "$pkg" ]; then
        echo "Checking $pkg..."
        if version=$(get_package_version "$pkg"); then
            package_versions["$pkg"]="$version"
        else
            echo "   Skipping $pkg (not found in Alpine)"
        fi
    fi
done

# Function to update package version in Dockerfile
update_package_in_dockerfile() {
    local dockerfile="$1"
    local package="$2"
    local new_version="$3"
    
    echo "Updating $package to $new_version in $dockerfile..."
    
    # Use sed to update the package version
    sed -i "s|${package}=[0-9][^[:space:]\\]*|${package}=${new_version}|g" "$dockerfile"
}

# Update all Dockerfiles with the latest package versions
echo "Updating Dockerfiles..."
for dockerfile in "${DOCKERFILES[@]}"; do
    if [ -f "$dockerfile" ]; then
        echo "Updating $dockerfile..."
        
        # Get packages from apk add blocks in this dockerfile using sed only
        dockerfile_packages=$(sed -n '/^RUN apk add/,/^$/{/^[[:space:]]*[a-z].*=/s/^[[:space:]]*\([a-z][a-z0-9-]*\)=.*/\1/p}' "$dockerfile" | sort | uniq)
        
        # Update each package found in this dockerfile
        for pkg in $dockerfile_packages; do
            if [ ! -z "$pkg" ] && [ ! -z "${package_versions[$pkg]}" ]; then
                update_package_in_dockerfile "$dockerfile" "$pkg" "${package_versions[$pkg]}"
            fi
        done
        
        echo "Updated $dockerfile"
    else
        echo "Warning: $dockerfile not found"
    fi
done

echo "Dockerfile updates completed!"

# Check if there are any changes
if git diff --quiet; then
    echo "No changes detected - all packages are already up to date"
    exit 0
else
    echo "Changes detected:"
    git diff --name-only
    echo "Ready for commit"
fi
