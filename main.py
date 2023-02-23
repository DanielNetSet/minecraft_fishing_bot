import os
import time

import cv2
import numpy
import win32con
import win32gui
import win32ui

bobber_day_1 = cv2.imread(os.path.join(
    "needle_image", "bobber_day_1.png"), cv2.IMREAD_UNCHANGED)
bobber_day_2 = cv2.imread(os.path.join(
    "needle_image", "bobber_day_2.png"), cv2.IMREAD_UNCHANGED)
bobber_night_1 = cv2.imread(os.path.join(
    "needle_image", "bobber_night_1.png"), cv2.IMREAD_UNCHANGED)
bobber_night_2 = cv2.imread(os.path.join(
    "needle_image", "bobber_night_2.png"), cv2.IMREAD_UNCHANGED)

needle_image = bobber_day_1

window_name = "Minecraft 1.19.3 - Singleplayer"
confdence = 0.7


def get_window_names():
    window_names = []

    def winEnumHandler(hwnd, ctx):
        if (win32gui.IsWindowVisible(hwnd)):
            window_names.append(win32gui.GetWindowText(hwnd))

    win32gui.EnumWindows(winEnumHandler, None)

    return [string for string in window_names if string != ""]


def get_window_handles(window_name):
    window_handles = []

    def winEnumHandler(window_handle, ctx):
        if (win32gui.IsWindowVisible(window_handle) and win32gui.GetWindowText(window_handle) == window_name):
            window_handles.append(window_handle)

    win32gui.EnumWindows(winEnumHandler, None)

    return window_handles


def capture_window(window_handle):
    if window_handle is None:
        window_handle = win32gui.GetDesktopWindow()

    window_dimensions = win32gui.GetWindowRect(window_handle)
    left = window_dimensions[0]
    top = window_dimensions[1]
    right = window_dimensions[2]
    bottom = window_dimensions[3]

    left_border = 8
    right_border = 8
    top_border = 30
    bottom_border = 8

    width = right - left - left_border - right_border
    height = bottom - top - top_border - bottom_border

    cropped_x = left_border
    cropped_y = top_border

    window_device_context = win32gui.GetWindowDC(window_handle)
    device_context_object = win32ui.CreateDCFromHandle(window_device_context)
    create_device_context = device_context_object.CreateCompatibleDC()
    data_bit_map = win32ui.CreateBitmap()
    data_bit_map.CreateCompatibleBitmap(device_context_object, width, height)
    create_device_context.SelectObject(data_bit_map)
    create_device_context.BitBlt(
        (0, 0), (width, height), device_context_object, (cropped_x, cropped_y), win32con.SRCCOPY)

    image = numpy.frombuffer(data_bit_map.GetBitmapBits(True), dtype="uint8")
    image.shape = (height, width, 4)

    device_context_object.DeleteDC()
    create_device_context.DeleteDC()
    win32gui.ReleaseDC(window_handle, window_device_context)
    win32gui.DeleteObject(data_bit_map.GetHandle())

    return image


def main():
    previous_time = time.time()

    while True:
        delta_time = time.time() - previous_time
        previous_time = time.time()

        if delta_time != 0:
            print(f"FPS: {1 / delta_time}")

        screenshot = capture_window(get_window_handles(window_name)[0])
        result = cv2.matchTemplate(
            screenshot, needle_image, cv2.TM_CCORR_NORMED)

        result_properties = cv2.minMaxLoc(result)
        min_value = result_properties[0]  # blackest pixle (0.0)
        max_value = result_properties[1]  # whietes pixle (1.0)
        min_location = result_properties[2]  # location of min_value (top left)
        max_location = result_properties[3]  # location of max_value (top left)

        if max_value >= confdence:
            cv2.rectangle(screenshot, (max_location[0] + 20, max_location[1] + 20), (max_location[0] -20 + needle_image.shape[0], max_location[1] - 20 + needle_image.shape[1]), (0, 255, 0), 2)

        cv2.imshow("Computer Vision Screenshot", screenshot)
        cv2.imshow("Computer vision Result", result)

        if cv2.waitKey(1) == ord("q"):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()

print("Done")
