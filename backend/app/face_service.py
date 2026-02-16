import io
import numpy as np
from PIL import Image
import logging

try:
    from facenet_pytorch import InceptionResnetV1, MTCNN
    import torch
    FACENET_AVAILABLE = True
except Exception:
    FACENET_AVAILABLE = False

logger = logging.getLogger(__name__)


class FaceService:
    def __init__(self):
        if FACENET_AVAILABLE:
            self.mtcnn = MTCNN(image_size=160)
            self.model = InceptionResnetV1(pretrained='vggface2').eval()
        else:
            logger.warning("facenet-pytorch not available; using fallback embeddings")

    def _preprocess(self, image_bytes: bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        return img

    def get_embedding(self, image_bytes: bytes) -> np.ndarray:
        img = self._preprocess(image_bytes)
        if FACENET_AVAILABLE:
            face = self.mtcnn(img)
            if face is None:
                raise ValueError("No face detected")
            with torch.no_grad():
                emb = self.model(face.unsqueeze(0)).numpy().astype(np.float32)
            return emb.flatten()
        else:
            # fallback: simple deterministic embedding from pixels (not secure)
            arr = np.array(img.resize((64, 64))).astype(np.float32)
            emb = np.mean(arr, axis=2).flatten()
            emb = emb / (np.linalg.norm(emb) + 1e-6)
            return emb.astype(np.float32)

    @staticmethod
    def compare_embeddings(a: np.ndarray, b: np.ndarray) -> float:
        a = a / (np.linalg.norm(a) + 1e-6)
        b = b / (np.linalg.norm(b) + 1e-6)
        return float(np.dot(a, b))

face_service = FaceService()
