import sys
from PIL import Image
import numpy as np
from scipy.ndimage import label, find_objects

# ============================
# Function Definitions
# ============================

def add_white_border(matrix, block_size):
    """
    Adds a white border around the binary QR code matrix.

    The border size is block_size * 4 pixels on each side.

    Args:
        matrix (np.ndarray): 2D binary array representing the QR code.
        block_size (int): Size of each block (pixels per module).

    Returns:
        np.ndarray: New binary array with the white border added.
    """
    # Input validation
    if not isinstance(matrix, np.ndarray):
        raise TypeError("Input matrix must be a numpy array.")
    if matrix.ndim != 2:
        raise ValueError("Input matrix must be 2-dimensional.")
    if not isinstance(block_size, int) or block_size <= 0:
        raise ValueError("block_size must be a positive integer.")

    # Calculate the border size based on block_size
    border_size = block_size * 4

    # Use numpy's pad function to add borders
    # Pad with 0s (white pixels)
    new_matrix = np.pad(
        matrix,
        pad_width=((border_size, border_size), (border_size, border_size)),
        mode='constant',
        constant_values=0
    )

    print(f"Added a white border of {border_size} pixels on all sides.")

    return new_matrix

def trim_zeros(matrix):
    """
    Trims the leading and trailing rows and columns that are entirely zeros from a binary matrix,
    specifically targeting zeros outside the largest connected component (assumed to be the QR code).

    Args:
        matrix (np.ndarray): 2D binary array (numpy array) to be trimmed.

    Returns:
        np.ndarray: Trimmed binary array containing only the QR code.
    """
    # Input validation
    if not isinstance(matrix, np.ndarray):
        raise TypeError("Input must be a numpy array.")
    if matrix.ndim != 2:
        raise ValueError("Input matrix must be 2-dimensional.")
    if matrix.size == 0:
        return matrix

    # Label connected components of 1s using 8-connectivity
    structure = np.ones((3, 3), dtype=int)
    labeled, num_features = label(matrix, structure=structure)

    if num_features == 0:
        # If there are no 1s, return an empty array
        return np.array([[]], dtype=matrix.dtype)

    # Find the largest connected component (assumed to be the QR code)
    component_sizes = np.bincount(labeled.flatten())
    component_sizes[0] = 0  # Exclude background
    largest_component = component_sizes.argmax()

    # Get the bounding box of the largest component
    slices = find_objects(labeled == largest_component)[0]
    row_min, row_max = slices[0].start, slices[0].stop
    col_min, col_max = slices[1].start, slices[1].stop

    # Slice the matrix to include only the relevant rows and columns
    trimmed_matrix = matrix[row_min:row_max, col_min:col_max]

    print(f"Trimmed image to shape: {trimmed_matrix.shape}")

    return trimmed_matrix

def estimate_qr_size(image_path):
    """
    Estimates the QR code grid size (number of modules per side) by analyzing
    the horizontal and vertical projection profiles of the image.

    Args:
        image_path (str): Path to the QR code image.

    Returns:
        int: Estimated number of modules per side of the QR code.
    """
    # Load and convert the image to grayscale
    image = Image.open(image_path).convert("L")
    image_array = np.array(image)

    # Compute the horizontal and vertical projection (sum of pixel values)
    horizontal_sum = np.sum(image_array, axis=1)
    vertical_sum = np.sum(image_array, axis=0)

    # Compute absolute differences to find transitions
    h_diff = np.abs(np.diff(horizontal_sum))
    v_diff = np.abs(np.diff(vertical_sum))

    # Determine dynamic thresholds using the 90th percentile
    h_threshold = np.percentile(h_diff, 90)
    v_threshold = np.percentile(v_diff, 90)

    # Find peaks where the difference exceeds the threshold
    h_peaks = np.where(h_diff > h_threshold)[0]
    v_peaks = np.where(v_diff > v_threshold)[0]

    # Estimate grid size (number of modules)
    # Number of modules = number of transitions + 1
    estimated_size = min(len(h_peaks), len(v_peaks)) + 1

    print(f"Estimated QR Grid Size: {estimated_size}x{estimated_size}")

    return estimated_size

def compute_block_size(image_width, image_height, grid_size):
    """
    Computes the optimal block size based on image dimensions and QR grid size.

    Args:
        image_width (int): Width of the image in pixels.
        image_height (int): Height of the image in pixels.
        grid_size (int): Number of modules per side of the QR code.

    Returns:
        int: Calculated block size (pixels per module).
    """
    block_size_width = image_width // grid_size
    block_size_height = image_height // grid_size
    block_size = min(block_size_width, block_size_height)

    print(f"Calculated Block Size: {block_size} pixels per module")

    return block_size

# ============================
# Main Processing Function
# ============================

def main():
    """
    Main function to process the QR code image:
    - Loads the image and converts it to a binary array.
    - Trims external zeros.
    - Estimates QR grid size and computes block size.
    - Adds a white border around the QR code.
    - Compresses the image into blocks.
    - Saves the binary and compressed arrays to files.
    - Saves visualizations of the binary and compressed images.
    """
    # Define the path to the QR code image
    image_path = '/home/teo/Facultate/ASC/cs_unibuc.png'

    # Load and convert the image to grayscale
    try:
        image = Image.open(image_path).convert('L')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        sys.exit(1)

    img = np.array(image)
    print("Original image shape:", img.shape)

    # Binary conversion: 0 = white (background), 1 = black (QR code)
    binarr = np.where(img > 128, 0, 1).astype(np.uint8)

    # Save the initial binary array for verification
    with open('binary1_file.out', "w") as g:
        for row in binarr:
            line = ' '.join(map(str, row))
            g.write(line + '\n')

    # Set NumPy print options for full array display (useful for debugging)
    np.set_printoptions(threshold=np.inf)

    # Trim external zeros to isolate the QR code
    binarr = trim_zeros(binarr)

    # Check if the trimmed array is empty
    if binarr.size == 0 or binarr.shape[0] == 0 or binarr.shape[1] == 0:
        print("Error: The trimmed binary array is empty.")
        sys.exit(1)  # Exit early to prevent further errors

    # Estimate the QR grid size
    grid_size = estimate_qr_size(image_path)

    # Compute block size based on grid size and image dimensions
    image_height, image_width = binarr.shape
    block_size = compute_block_size(image_width, image_height, grid_size)

    # Ensure block_size is at least 1 to prevent division by zero
    block_size = max(1, block_size)

    # Add a white border around the QR code
    binarr = add_white_border(binarr, block_size)
    print("Image shape after adding white border:", binarr.shape)

    # Compute new dimensions after dividing into blocks
    new_height = binarr.shape[0] // block_size
    new_width = binarr.shape[1] // block_size

    print(f"New dimensions after block processing: {new_height} x {new_width}")

    # Initialize the compressed array to store block-wise results
    compressed_arr = np.zeros((new_height, new_width), dtype=int)

    # Process each block to compress the image
    for i in range(new_height):
        for j in range(new_width):
            # Extract the current block
            block = binarr[
                i * block_size : (i + 1) * block_size,
                j * block_size : (j + 1) * block_size
            ]

            # Compute the mean of the block
            if block.size == 0:
                # Default to white if block is empty
                compressed_arr[i, j] = 0
            else:
                # Set to 1 (black) if mean >= 0.5, else 0 (white)
                compressed_arr[i, j] = 1 if np.mean(block) >= 0.5 else 0

    # Save the compressed binary array to a file for verification
    with open('binary_file.out', "w") as g:
        for row in compressed_arr:
            line = ' '.join(map(str, row))
            g.write(line + '\n')

    # Reset NumPy print options to default
    np.set_printoptions(threshold=1000)

    # Save the binary image visualization
    binimg_array = (1 - binarr) * 255  # Invert and scale to 255 for correct colors
    binimg = Image.fromarray(binimg_array.astype(np.uint8))
    temp_path = '/home/teo/Facultate/ASC/temp_binary.png'
    binimg.save(temp_path)
    print(f"Saved binary image at {temp_path}")


# ============================
# Entry Point
# ============================

if __name__ == '__main__':
    main()
