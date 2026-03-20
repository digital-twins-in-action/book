import numpy as np
import matplotlib.pyplot as plt


def create_transformation_matrix(
    origin_easting, origin_northing, rotation_angle_degrees
):
    """
    Create a 3x3 transformation matrix for converting local coordinates to UTM

    Parameters:
    - origin_easting: UTM easting coordinate of the local origin
    - origin_northing: UTM northing coordinate of the local origin
    - rotation_angle_degrees: rotation angle in degrees (positive is counterclockwise)

    Returns:
    - 3x3 transformation matrix
    """
    # Convert angle to radians
    theta = np.radians(rotation_angle_degrees)

    # Create the transformation matrix
    # [ cos(θ) -sin(θ)  tx ]
    # [sin(θ)  cos(θ)  ty ]
    # [   0       0      1 ]

    matrix = np.array(
        [
            [np.cos(theta), -np.sin(theta), origin_easting],
            [np.sin(theta), np.cos(theta), origin_northing],
            [0, 0, 1],
        ]
    )

    return matrix


def transform_coordinates(local_coords, transform_matrix):
    """
    Transform local coordinates to UTM coordinates

    Parameters:
    - local_coords: Nx2 array of local coordinates (x, y)
    - transform_matrix: 3x3 transformation matrix

    Returns:
    - Nx2 array of UTM coordinates (easting, northing)
    """
    # Add a column of ones to make the coordinates homogeneous
    homogeneous_coords = np.hstack([local_coords, np.ones((local_coords.shape[0], 1))])

    # Apply the transformation: (matrix * coords^T)^T
    utm_coords = (transform_matrix @ homogeneous_coords.T).T

    # Return just the easting and northing (drop the homogeneous coordinate)
    return utm_coords[:, :2]


# Example usage:
if __name__ == "__main__":
    # UTM coordinates of the local origin
    origin_easting = 471519  # meters
    origin_northing = 7977628  # meters

    # Rotation angle (degrees)
    rotation_angle = 30  # positive is counterclockwise

    # Create the transformation matrix
    transform_matrix = create_transformation_matrix(
        origin_easting, origin_northing, rotation_angle
    )

    # Print the transformation matrix
    print("Transformation Matrix:")
    print(transform_matrix)

    # Create some local coordinates for demonstration
    local_coords = np.array(
        [
            [0, 0],  # origin
            [100, 0],  # 100m east
            [0, 100],  # 100m north
            [100, 100],  # 100m northeast
        ]
    )

    # Transform the coordinates
    utm_coords = transform_coordinates(local_coords, transform_matrix)

    # Print the results
    print("\nLocal Coordinates (x, y) and UTM Coordinates (easting, northing):")
    for i in range(len(local_coords)):
        print(
            f"Local: ({local_coords[i][0]}, {local_coords[i][1]}) → UTM: ({utm_coords[i][0]:.1f}, {utm_coords[i][1]:.1f})"
        )

    # Visualize the transformation
    plt.figure(figsize=(10, 8))

    # Plot local coordinates
    plt.subplot(1, 2, 1)
    plt.scatter(local_coords[:, 0], local_coords[:, 1], color="blue")
    for i, (x, y) in enumerate(local_coords):
        plt.annotate(f"P{i}", (x, y), xytext=(5, 5), textcoords="offset points")
    plt.grid(True)
    plt.axis("equal")
    plt.xlabel("Local X (m)")
    plt.ylabel("Local Y (m)")
    plt.title("Local Coordinate System")

    # Plot UTM coordinates
    plt.subplot(1, 2, 2)
    plt.scatter(utm_coords[:, 0], utm_coords[:, 1], color="red")
    for i, (e, n) in enumerate(utm_coords):
        plt.annotate(f"P{i}", (e, n), xytext=(5, 5), textcoords="offset points")
    plt.grid(True)
    plt.axis("equal")
    plt.xlabel("UTM Easting (m)")
    plt.ylabel("UTM Northing (m)")
    plt.title("UTM Coordinate System")

    plt.tight_layout()
    plt.savefig("coordinate_transformation.png")
    plt.show()
