import os
import time

import cv2
import pytesseract
import numpy
import win32con
import win32gui
from pynput.mouse import Button, Controller
import win32ui

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

window_name = "Minecraft 1.19.3 - Singleplayer"


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

        if len(get_window_handles(window_name)) == 0:
            print("error: no windows not found")
            break

        screenshot = capture_window(get_window_handles(window_name)[0])

        text = pytesseract.image_to_string(cv2.threshold(cv2.cvtColor(
            screenshot, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])

        if "fishing bobber splashes" in text.lower():
            print('---------------------- FOUND TEXT')
            Controller().click(Button.right)
            time.sleep(1.4)
            Controller().click(Button.right)

        cv2.imshow("Computer Vision Screenshot", screenshot)

        if cv2.waitKey(1) == ord("q"):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()

print("Done")
