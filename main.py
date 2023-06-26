import time

import cv2
import numpy
import pynput
import pytesseract
import win32con
import win32gui
import win32ui

phrase = "bobber splashes"
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


def get_window_names():
    window_names = []

    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            window_names.append(win32gui.GetWindowText(hwnd))

    win32gui.EnumWindows(winEnumHandler, None)
    return [string for string in window_names if string != ""]


def get_window_handles():
    window_handles = []

    def winEnumHandler(window_handle, ctx):
        if (win32gui.IsWindowVisible(window_handle) and
                win32gui.GetWindowText(window_handle)[0:9] == "Minecraft"):
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
    x = width * 3 // 4
    y = height * 3 // 4
    width = width // 4
    height = height // 4
    cropped_x = x
    cropped_y = y
    window_device_context = win32gui.GetWindowDC(window_handle)
    device_context_object = win32ui.CreateDCFromHandle(window_device_context)
    create_device_context = device_context_object.CreateCompatibleDC()
    data_bit_map = win32ui.CreateBitmap()
    data_bit_map.CreateCompatibleBitmap(device_context_object, width, height)
    create_device_context.SelectObject(data_bit_map)
    create_device_context.BitBlt(
        (0, 0),
        (width, height),
        device_context_object,
        (cropped_x, cropped_y),
        win32con.SRCCOPY)

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
            print(f"fps: {1 / delta_time}")

        if len(get_window_handles()) == 0:
            print("error: no windows not found")
            break

        screenshot = cv2.cvtColor(capture_window(
            get_window_handles()[0]), cv2.COLOR_BGR2GRAY)
        screenshot = capture_window(get_window_handles()[0])
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(cv2.threshold(
            screenshot,
            0,
            255,
            cv2.THRESH_BINARY
            + cv2.THRESH_OTSU)[1])

        if phrase in text.lower():
            print("fish on")
            pynput.mouse.Controller().click(pynput.mouse.Button.right)
            time.sleep(0.5)
            pynput.mouse.Controller().click(pynput.mouse.Button.right)
            time.sleep(4)

        cv2.imshow("Computer Vision", screenshot)

        if cv2.waitKey(1) == ord("q"):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()
