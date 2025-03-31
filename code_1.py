import streamlit as st
from PIL import Image
# --- Background Removal Logic ---
# Using 'rembg' as an example. Replace if you have your own method.
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    # Define a dummy function if rembg isn't installed or you want to use your own later
    def remove(img_bytes):
        st.error("`rembg` library not found. Background removal placeholder active.")
        # In a real placeholder, you might return img_bytes or raise an error
        # For now, returning original bytes to allow app structure to work
        return img_bytes
# ---------------------------------
from io import BytesIO
import os # To help generate filename

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Simple Background Remover",
    page_icon="✂️",
    layout="centered" # Keep it simple and centered
)

# --- Helper Function for Background Removal ---
# Takes a PIL Image, returns a PIL Image
@st.cache_data # Cache the result to avoid re-processing on minor UI interaction
def remove_background_from_bytes(_image_bytes: bytes) -> bytes | None:
    """Removes the background from a PIL Image object using the chosen method."""
    try:
        # Convert PIL Image to bytes for rembg (or your function if it expects bytes)
        # Use the remove function (rembg or your custom one)
        output_bytes = remove(_image_bytes)
        return output_bytes
    except Exception as e:
        st.error(f"Error during background removal: {e}")
        # Return None to indicate failure
        return None

# --- Streamlit App UI ---
st.title("✂️ Simple Background Remover")
st.write("Upload an image (JPG, JPEG, or PNG) to remove its background.")
st.write("---")

uploaded_file = st.file_uploader(
    "Choose an image...",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False # Only allow one file at a time
    )

if uploaded_file is not None:
    # Read the uploaded image using PIL
    input_image = Image.open(uploaded_file)

    # Display the original image in the first column
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Original Image")
        st.image(input_image, caption="Your Upload", use_column_width=True)

    # Process the image (with spinner)
    with st.spinner('Removing background... Please wait.'):
        # Call the helper function
        output_image = remove_background_from_bytes(input_image) # Uses caching

    # Display the result in the second column
    with col2:
        if output_image:
            st.write("### Background Removed")
            st.image(output_image, caption="Processed Image", use_column_width=True)

            # --- Download Options ---
            st.write("---") # Separator before download
            st.write("#### Download Result")

            # Select download format
            download_format = st.selectbox(
                "Select download format",
                ["PNG", "JPG"],
                key="format_select" # Unique key for the widget
                )

            # Prepare image bytes for download based on selected format
            buf_out = BytesIO()
            output_filename = f"bg_removed_{os.path.splitext(uploaded_file.name)[0]}.{download_format.lower()}"
            save_format = 'JPEG' if download_format == 'JPG' else 'PNG'

            try:
                if save_format == 'JPEG':
                    # Handle JPG: Convert RGBA to RGB with a white background if needed
                    if output_image.mode == 'RGBA':
                        # Create a white background image
                        bg = Image.new("RGB", output_image.size, (255, 255, 255))
                        # Paste the image onto the background using the alpha channel as mask
                        bg.paste(output_image, mask=output_image.split()[3])
                        bg.save(buf_out, format=save_format, quality=95) # Good quality for JPG
                    else: # If already RGB or other non-alpha mode
                         output_image.convert('RGB').save(buf_out, format=save_format, quality=95)
                else: # PNG: Save directly, preserves transparency
                    output_image.save(buf_out, format=save_format)

                st.download_button(
                    label=f"Download as {download_format}",
                    data=buf_out.getvalue(),
                    file_name=output_filename,
                    mime=f"image/{download_format.lower()}",
                    key="download_button" # Unique key
                )
            except Exception as e:
                st.error(f"Error preparing download: {e}")

        else:
            # If processing failed
            st.error("Could not process the image. Please try another one or check the logs.")

else:
    st.info("☝️ Upload an image file to get started.")

# --- Sidebar with Library Info (Optional but good practice) ---
st.sidebar.header("Info")
st.sidebar.markdown("""
This app uses Python and Streamlit to remove backgrounds from images.
""")
st.sidebar.header("Libraries Used")
st.sidebar.markdown(f"""
- **streamlit**: Web App Framework
- **Pillow**: Image Processing
- **rembg**: Background Removal Engine {'**(Using Example)**' if REMBG_AVAILABLE else '**(`rembg` not found - install or replace logic)**'}
- **io, os**: Standard Libraries
""")
st.sidebar.header("Installation")
st.sidebar.code("pip install streamlit pillow rembg", language="bash")
if not REMBG_AVAILABLE:
    st.sidebar.warning("`rembg` not found. Install it or replace the background removal function in the code.")