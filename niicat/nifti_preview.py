import numpy as np
import nibabel as nb
from PIL import Image, ImageDraw, ImageFont


def _font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _normalize_slice(data):
    data = np.asarray(data)
    finite = np.isfinite(data)
    if not finite.any():
        return np.zeros(data.shape, dtype=np.uint8)

    minimum = np.min(data[finite])
    maximum = np.max(data[finite])
    if maximum == minimum:
        return np.zeros(data.shape, dtype=np.uint8)

    normalized = (
        np.nan_to_num(data, nan=minimum, posinf=maximum, neginf=minimum) - minimum
    ) * (255.0 / (maximum - minimum))
    return np.clip(normalized, 0, 255).astype(np.uint8)


def _draw_dotted_line(draw, xy, fill, width, dash):
    x1, y1, x2, y2 = xy
    if x1 == x2:
        for y in range(y1, y2 + 1, dash * 2):
            draw.line((x1, y, x2, min(y + dash, y2)), fill=fill, width=width)
    else:
        for x in range(x1, x2 + 1, dash * 2):
            draw.line((x, y1, min(x + dash, x2), y2), fill=fill, width=width)


def _paste_slice(canvas, data, box, pixel_aspect, crosshair):
    left, top, right, bottom = box
    box_width = right - left
    box_height = bottom - top
    source_height, source_width = data.shape
    display_ratio = source_width / (source_height * pixel_aspect)

    if box_width / box_height > display_ratio:
        height = box_height
        width = max(1, round(height * display_ratio))
    else:
        width = box_width
        height = max(1, round(width / display_ratio))

    x = left + (box_width - width) // 2
    y = top + (box_height - height) // 2
    image = Image.fromarray(_normalize_slice(data))
    image = image.resize((width, height), Image.Resampling.BILINEAR).convert("RGB")
    canvas.paste(image, (x, y))

    crosshair_x, crosshair_y = crosshair
    line_x = x + round(crosshair_x * max(width - 1, 0))
    line_y = y + round(crosshair_y * max(height - 1, 0))
    draw = ImageDraw.Draw(canvas)
    line_width = max(1, canvas.width // 1000)
    dash = max(2, canvas.width // 250)
    _draw_dotted_line(draw, (x, line_y, x + width - 1, line_y), "red", line_width, dash)
    _draw_dotted_line(draw, (line_x, y, line_x, y + height - 1), "red", line_width, dash)
    return x, y, width, height


def _load_data(image):
    data = np.asanyarray(image.dataobj)
    if data.dtype.fields is not None:
        from numpy.lib import recfunctions as rfn

        data = rfn.structured_to_unstructured(data)
        if data.ndim == 4:
            data = data[:, :, :, 0]
    elif data.ndim == 4:
        data = data[:, :, :, 0]
    return data


def save_nifti_preview(filename, output, dpi=200, slice_num=None):
    image = nb.load(filename)
    data = _load_data(image)
    if data.ndim != 3:
        raise ValueError(f"Expected a 3D or 4D NIfTI image, got shape {data.shape}")

    length_x, length_y, length_z = data.shape
    if slice_num is not None:
        minimum_dimension = min(length_x, length_y, length_z)
        if slice_num < 0 or slice_num >= minimum_dimension:
            raise ValueError(
                f"Slice number {slice_num} is out of bounds. "
                f"Must be between 0 and {minimum_dimension - 1}"
            )
        middle_x = length_x - 1 - slice_num
        middle_y = length_y - 1 - slice_num
        middle_z = length_z - 1 - slice_num
    else:
        middle_x = length_x // 2
        middle_y = length_y // 2
        middle_z = length_z // 2

    spacing_x, spacing_y, spacing_z = image.header["pixdim"][1:4]
    width = round(5 * dpi)
    height = round(4 * dpi)
    half_width = width // 2
    half_height = height // 2
    canvas = Image.new("RGB", (width, height), "black")

    _paste_slice(
        canvas,
        np.rot90(data[:, middle_y, :]),
        (0, 0, half_width, half_height),
        spacing_z / spacing_x,
        (middle_x / max(length_x - 1, 1), middle_z / max(length_z - 1, 1)),
    )
    _paste_slice(
        canvas,
        np.rot90(data[middle_x, :, :]),
        (half_width, 0, width, half_height),
        spacing_z / spacing_y,
        (middle_y / max(length_y - 1, 1), middle_z / max(length_z - 1, 1)),
    )
    axial_box = _paste_slice(
        canvas,
        np.rot90(data[:, :, middle_z]),
        (0, half_height, half_width, height),
        spacing_y / spacing_x,
        (middle_x / max(length_x - 1, 1), middle_y / max(length_y - 1, 1)),
    )

    qform_x = image.get_qform()[0, 0]
    sform_x = image.get_sform()[0, 0]
    if sform_x < 0 and (qform_x == 0 or qform_x < 0):
        orientation = "R"
    elif sform_x > 0 and (qform_x == 0 or qform_x > 0):
        orientation = "L"
    else:
        orientation = ""

    draw = ImageDraw.Draw(canvas)
    label_font = _font(max(9, round(9 * dpi / 72)))
    axial_x, axial_y, _, axial_height = axial_box
    draw.text(
        (axial_x + 2, axial_y + axial_height - label_font.size - 2),
        orientation,
        fill="red",
        font=label_font,
    )

    minimum = np.nanmin(data)
    maximum = np.nanmax(data)
    if np.isfinite(minimum) and np.isfinite(maximum):
        range_text = f"{np.round(minimum, 2)} - {np.round(maximum, 2)}"
    else:
        range_text = "nan - nan"

    sform = np.array2string(np.round(image.get_sform(), 2))
    qform = np.array2string(np.round(image.get_qform(), 2))
    text = (
        f"Dimensions: {length_x} x {length_y} x {length_z}\n"
        f"Spacing: {spacing_x:.2f} x {spacing_y:.2f} x {spacing_z:.2f} mm\n"
        f"Volumes: {image.header['dim'][4]}\n"
        f"Data type: {image.header.get_data_dtype()}\n"
        f"Range: {range_text}\n\n"
        f"sform code:\n{sform}\n\n"
        f"qform code:\n{qform}"
    )
    text_font = _font(max(8, round(6 * dpi / 72)))
    draw.multiline_text(
        (half_width + round(0.075 * width), half_height + round(0.025 * height)),
        text,
        fill="white",
        font=text_font,
        spacing=max(1, round(dpi / 100)),
    )

    canvas.save(output, format="PNG", compress_level=3)
