from paddleocr import PaddleOCR
import cv2
import re
import numpy as np

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

def noise_removal(img):
    """
    Removes noise from the image using morphological operations and blurring.
    """
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.medianBlur(img, 3)
    return img

def extract_passport_details(text):
    """
    Extracts details such as ID type, names, nationality, DOB, and more from OCR text.
    """
    details = {}

    # Extract ID type
    if "PASSPORT" in text:
        details['ID Type'] = "PASSPORT"
    elif "LICENSE" in text:
        details['ID Type'] = "LICENSE"

    # Extract Last and First Name using MRZ format
    name_match = re.search(r"P<\w{3}(\w+)<([\w<]+)", text)
    if name_match:
        details['Last Name'] = name_match.group(1).strip()
        details['First Name'] = name_match.group(2).replace('<', ' ').strip()

    # For license
    name_match = re.search(r'\b1\n([A-Z]+)', text)
    if name_match:
        details['Name'] = name_match.group(1)

    # Extract Nationality
    nation_match = re.search(r"P<([A-Z]{3})", text)
    if nation_match:
        code = nation_match.group(1)
        nationality_mapping = {
            "GBR": "BRITISH",
            "CHN": "HONG KONG",
            "IND": "INDIAN",
            "USA": "AMERICAN"
        }
        details["Nationality"] = nationality_mapping.get(code, "Nationality code not recognized.")

    # Extract Passport Number
    passport_match = re.search(r"\n(\d{9})", text)
    if passport_match:
        details["Passport Number"] = passport_match.group(1)

    # Extract Driver's License Number
    dl_num = re.search(r'\b(W\d{6})\b', text)
    if dl_num:
        details["DL Number"] = dl_num.group(1)

    # Extract Gender
    gender_match = re.search(r"\d{6}([MF<])", text) or re.search(r'\bSex\s?([MF])\b', text)
    if gender_match:
        details["Gender"] = gender_match.group(1)

    # Extract Date of Birth
    dob_match = re.search(r'\b(\d{1,2}[A-Za-z]{3}\s\d{4})\b', text) or re.search(r'\b3D0B(\d{2}/\d{2}/\d{4})\b', text)
    if dob_match:
        details['DOB'] = dob_match.group(1)

    # Extract Place of Birth
    pob_match = re.search(r'Place of birth.*?\nSex.*?\n(.+)', text)
    if pob_match:
        details['Place of Birth'] = pob_match.group(1)

    # Extract Date of Issue
    doi_match = re.search(r'\b(\d{1,2}\s[A-Za-z]{3}\s\d{4})\b', text)
    if doi_match:
        details['Date of Issue'] = doi_match.group(1)

    # Extract Expiry Date
    expiry_match = re.search(r'\b(\d{1,2}\s[A-Za-z]{3}\s\d{4})\b', text) or re.search(r'\bExp(\d{2}/\d{2}/\d{4})', text)
    if expiry_match:
        details['Expiry Date'] = expiry_match.group(1)

    # Extract Address (specific for licenses)
    address_match = re.search(r'1\n\n([^\n]+)\n([^\n]+)', text)
    if address_match:
        details['Address Line 1'] = address_match.group(1).strip()
        details['Address Line 2'] = address_match.group(2).strip()

    return details

def process_image(img_path):
    """
    Processes the image to extract text using OCR and parse details from the text.
    """
    # Load the image
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.threshold(img, 200, 230, cv2.THRESH_BINARY)[1]
    img = noise_removal(img)

    # Perform OCR
    results = ocr.ocr(img_path)
    text = "\n".join([line[1][0] for line in results[0]])

    # Extract details
    details = extract_passport_details(text)
    return details
