import base64


class LocalImageProvider:
    def generate_from_text(self, text: str) -> dict:
        # 1x1 PNG (transparent) placeholder for local modality integration.
        one_pixel_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00"
            b"\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return {
            "mimeType": "image/png",
            "dataBase64": base64.b64encode(one_pixel_png).decode("ascii"),
            "promptUsed": text[:200],
        }

