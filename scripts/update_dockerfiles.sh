#!/bin/bash
set -e

echo "Starting Dockerfile package updates..."

# Find all Dockerfiles in the images directory
echo "Searching for Dockerfiles in images directory..."
DOCKERFILES=($(find images -name "Dockerfile" -type f))
echo "Found Dockerfiles: ${DOCKERFILES[*]}"

# Function to extract BASE_IMAGE from Dockerfile
extract_base_image() {
    local dockerfile="$1"

    echo "Extracting BASE_IMAGE from $dockerfile..." >&2
    local base_image=$(grep -E '^ARG BASE_IMAGE=' "$dockerfile" | sed 's/^ARG BASE_IMAGE=//' | tr -d '"')

    if [ -z "$base_image" ]; then
        echo "Error: Could not find BASE_IMAGE in $dockerfile" >&2
        return 1
    fi

    echo "   Base image: $base_image" >&2
    echo "$base_image"
}

# Function to get latest package version
get_package_version() {
    local package_name="$1"
    local base_image="$2"

    echo "Checking latest version for $package_name using $base_image..." >&2
    local version=$(docker run --rm "$base_image" sh -c "
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

# Function to extract packages from a Dockerfile
extract_packages_from_dockerfile() {
    local dockerfile="$1"

    echo "Extracting packages from $dockerfile..." >&2
    # Extract packages from multi-line apk add blocks
    local packages=$(sed -n '/^RUN apk add/,/^$/{/^[[:space:]]*[a-z].*=/s/^[[:space:]]*\([a-z][a-z0-9-]*\)=.*/\1/p}' "$dockerfile" | sort | uniq)
    echo "$packages"
}

# Function to update package version in Dockerfile
update_package_in_dockerfile() {
    local dockerfile="$1"
    local package="$2"
    local new_version="$3"

    echo "Updating $package to $new_version in $dockerfile..."

    # Use sed to update the package version
    sed -i "s|${package}=[0-9][^[:space:]\\]*|${package}=${new_version}|g" "$dockerfile"
}

# Process each Dockerfile individually
for dockerfile in "${DOCKERFILES[@]}"; do
    if [ ! -f "$dockerfile" ]; then
        echo "Warning: $dockerfile not found, skipping..."
        continue
    fi

    echo "=========================================="
    echo "Processing $dockerfile..."
    echo "=========================================="

    # Extract BASE_IMAGE from this Dockerfile
    if ! base_image=$(extract_base_image "$dockerfile"); then
        echo "Error: Failed to extract BASE_IMAGE from $dockerfile, skipping..."
        continue
    fi

    # Get the Alpine version from the base image
    echo "Checking Alpine version in base image..."
    ALPINE_VERSION=$(docker run --rm "$base_image" cat /etc/alpine-release)
    echo "   Alpine version: $ALPINE_VERSION"

    # Extract packages from this Dockerfile
    dockerfile_packages=$(extract_packages_from_dockerfile "$dockerfile")

    if [ -z "$dockerfile_packages" ]; then
        echo "   No packages found in $dockerfile, skipping..."
        continue
    fi

    # Convert new-line, space-separated to comma-separated for display
    dockerfile_packages_csv=$(echo "$dockerfile_packages" | tr '\n' ',' | tr -s ' ' ',' | sed 's/^,//;s/,$//' | sed 's/,/, /g')
    echo "Found packages in $dockerfile: $dockerfile_packages_csv"

    # Get latest versions for packages in this Dockerfile
    echo "Fetching latest versions for packages in $dockerfile..."
    declare -A package_versions
    for pkg in $dockerfile_packages; do
        if [ ! -z "$pkg" ]; then
            echo "Checking $pkg..."
            if version=$(get_package_version "$pkg" "$base_image"); then
                package_versions["$pkg"]="$version"
            else
                echo "   Skipping $pkg (not found in Alpine)"
            fi
        fi
    done

    # Update packages in this Dockerfile
    echo "Updating packages in $dockerfile..."
    for pkg in $dockerfile_packages; do
        if [ ! -z "$pkg" ] && [ ! -z "${package_versions[$pkg]}" ]; then
            update_package_in_dockerfile "$dockerfile" "$pkg" "${package_versions[$pkg]}"
        fi
    done

    echo "Completed processing $dockerfile"
    echo ""
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
