import cv2
import numpy as np

def apply_filter(gray_img, filter_type, kernel_size):
    """Applies noise smoothing filters."""
    if kernel_size % 2 == 0:
        kernel_size += 1  # Force odd number
        
    if filter_type == 'g':
        return cv2.GaussianBlur(gray_img, (kernel_size, kernel_size), 0)
    elif filter_type == 'm':
        return cv2.medianBlur(gray_img, kernel_size)
    return gray_img

def apply_edge_detection(gray_img, edge_type, kernel_size, canny_low, canny_high):
    """Applies edge detection techniques."""
    if kernel_size % 2 == 0:
        kernel_size += 1
        
    if edge_type == 's':
        sobelx = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(sobelx**2 + sobely**2)
        return np.uint8(np.clip(mag, 0, 255))
    elif edge_type == 'l':
        lap = cv2.Laplacian(gray_img, cv2.CV_64F, ksize=kernel_size)
        return np.uint8(np.clip(np.absolute(lap), 0, 255))
    elif edge_type == 'c':
        return cv2.Canny(gray_img, canny_low, canny_high)
    return gray_img

def sanitize_filename(filename):
    """Removes spaces and invalid characters from filename safely."""
    filename = filename.replace(' ', '_')
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    sanitized = "".join([c for c in filename if c in allowed_chars])
    if not sanitized:
        sanitized = "processed_output"
    return sanitized + ".png"

def main():
    image_path = '1000_F_308359163_SQHV1pdPwaZwVZlV3dwpcOb1V18TLMwe.jpg' # Adjust to point to your images folder
    original = cv2.imread(image_path)

    if original is None:
        print(f"Error: Could not open or find the image at '{image_path}'.")
        return

    # App States
    filter_type = 'None'      # 'g' for Gaussian, 'm' for Median, 'None'
    edge_type = 's'          # 's' for Sobel, 'c' for Canny, 'l' for Laplacian
    kernel_size = 3
    canny_low = 50
    canny_high = 150
    
    # State history stack for the Undo feature
    history = []

    print("=" * 60)
    print(" INTERACTIVE EDGE DETECTION & FILTER CONTROLS ")
    print("=" * 60)
    print(" [s] Sobel Edge Detector    | [1] Decrease Kernel (-2)")
    print(" [c] Canny Edge Detector    | [2] Increase Kernel (+2)")
    print(" [l] Laplacian Detector     | [u] Undo Last Change")
    print(" ---------------------------| [o] Reset App State")
    print(" [g] Gaussian Blur Filter   | [i] Canny Low Thresh (+10)")
    print(" [m] Median Blur Filter     | [d] Canny Low Thresh (-10)")
    print(" [f] Clear Active Filter    | [w] Canny High Thresh (+10)")
    print("                            | [x] Canny High Thresh (-10)")
    print(" [q] Proceed to Save & Quit")
    print("=" * 60)

    while True:
        # Pre-process image to Grayscale
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        
        # 1. Pipeline execution: Filter -> Edge Detection
        filtered = apply_filter(gray, filter_type, kernel_size)
        processed = apply_edge_detection(filtered, edge_type, kernel_size, canny_low, canny_high)
        
        # Convert processed single-channel gray back to 3-channels so we can stitch side-by-side
        processed_bgr = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        
        # Merge original and processed together horizontally
        display_canvas = np.hstack((original, processed_bgr))
        
        # Overlay visual parameters text on top of the image display frame
        status_text = f"Filter: {filter_type.upper()} (K:{kernel_size}) | Edge: {edge_type.upper()} | Canny: L:{canny_low} H:{canny_high}"
        cv2.putText(display_canvas, status_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_canvas, "ORIGINAL", (15, display_canvas.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(display_canvas, "PROCESSED", (original.shape[1] + 15, display_canvas.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("Image Processing Sandbox", display_canvas)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Capture current configuration states before mutations happen (For Undo functionality)
        if key in [ord('s'), ord('c'), ord('l'), ord('g'), ord('m'), ord('f'), ord('1'), ord('2'), ord('i'), ord('d'), 82, 84, ord('w'), ord('x')]:
            current_state = (filter_type, edge_type, kernel_size, canny_low, canny_high)
            # Only record if it differs from the last stored state to keep history clean
            if not history or history[-1] != current_state:
                history.append(current_state)

        # Handle Keyboard Inputs
        if key == ord('q'):
            break
        elif key == ord('o'):
            print("→ Settings Reset to Default")
            filter_type, edge_type, kernel_size, canny_low, canny_high = 'None', 's', 3, 50, 150
            history.clear()
        elif key == ord('u'):
            if history:
                filter_type, edge_type, kernel_size, canny_low, canny_high = history.pop()
                print("→ Step Undone")
            else:
                print("→ Nothing left to undo!")
        elif key == ord('s'):
            print("→ Method Changed: Sobel")
            edge_type = 's'
        elif key == ord('c'):
            print("→ Method Changed: Canny")
            edge_type = 'c'
        elif key == ord('l'):
            print("→ Method Changed: Laplacian")
            edge_type = 'l'
        elif key == ord('g'):
            print("→ Filter Switched: Gaussian Blur")
            filter_type = 'g'
        elif key == ord('m'):
            print("→ Filter Switched: Median Blur")
            filter_type = 'm'
        elif key == ord('f'):
            print("→ Filter Removed")
            filter_type = 'None'
        elif key == ord('2'):
            kernel_size = min(15, kernel_size + 2)
            print(f"→ Kernel Increased: {kernel_size}")
        elif key == ord('1'):
            kernel_size = max(3, kernel_size - 2)
            print(f"→ Kernel Decreased: {kernel_size}")
        elif key == ord('i'):
            canny_low = min(255, canny_low + 10)
            print(f"→ Canny Low Threshold Raised: {canny_low}")
        elif key == ord('d'):
            canny_low = max(0, canny_low - 10)
            print(f"→ Canny Low Threshold Lowered: {canny_low}")
        elif key == 82 or key == ord('w'):  # Up Arrow or 'w'
            canny_high = min(255, canny_high + 10)
            print(f"→ Canny High Threshold Raised: {canny_high}")
        elif key == 84 or key == ord('x'):  # Down Arrow or 'x'
            canny_high = max(0, canny_high - 10)
            print(f"→ Canny High Threshold Lowered: {canny_high}")

    cv2.destroyAllWindows()
    
    # Save Image Flow
    user_filename = input("\nEnter custom name to save your edge-detected image: ").strip()
    safe_name = sanitize_filename(user_filename)
    
    save_path = "images/" + safe_name
    success = cv2.imwrite(save_path, processed)
    if success:
        print(f"\n🎉 Success! Result saved securely to: {save_path}")
    else:
        print("\n❌ Error: Write failed. Could not output image file. Verify 'images/' folder exists.")

if __name__ == "__main__":
    main()
