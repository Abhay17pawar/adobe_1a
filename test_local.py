#!/usr/bin/env python3
"""
Note: This local test script is deprecated.
For testing, please use the Docker-based test script instead:

    ./test.sh

The tester will use Docker for official evaluation.
"""

def main():
    """Main function that redirects to Docker testing"""
    print("⚠️  Local Python testing is not supported.")
    print("📦 Please use Docker testing instead:")
    print("")
    print("   ./test.sh")
    print("")
    print("This ensures consistency with the official testing environment.")
    print("All dependencies and testing should be done via Docker.")

if __name__ == "__main__":
    main()
