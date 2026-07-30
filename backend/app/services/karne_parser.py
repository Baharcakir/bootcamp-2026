import json
import io
import google.generativeai as genai
from PIL import Image

def parse_report_card(image_bytes: bytes) -> dict:
    """
    Yüklenen karne fotoğrafını Gemini Vision'a gönderir 
    ve ders bazlı doğru, yanlış, net verisini JSON olarak döndürür.
    """
    # Görseli PIL formatına çevir
    image = Image.open(io.BytesIO(image_bytes))
    
    # Gemini modeli
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Sen bir YKS/TYT deneme karnesi okuyucususun. 
    Verilen karne görselinden tüm derslerin doğru, yanlış ve net sayılarını çıkar.
    
    Yalnızca ve yalnızca geçerli bir JSON objesi döndür. Markdown bloğu veya ekstra açıklama yazma.
    Örnek JSON Yapısı:
    {
      "turkce": {"dogru": 30, "yanlis": 5, "net": 28.75},
      "matematik": {"dogru": 25, "yanlis": 2, "net": 24.5},
      "fen": {"dogru": 15, "yanlis": 3, "net": 14.25},
      "sosyal": {"dogru": 18, "yanlis": 2, "net": 17.5}
    }
    """
    
    response = model.generate_content([prompt, image])
    
    # JSON çıktısını temizleyip Python sözlüğüne (dict) çevir
    clean_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(clean_text)