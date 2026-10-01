import os, sys, json, base64, io, urllib.request, concurrent.futures as cf
from PIL import Image

KEY = os.environ["OPENAI_API_KEY"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "img")
os.makedirs(OUT, exist_ok=True)

STYLE = ("Authentic editorial photograph, shot on a full-frame camera with a 35mm lens, natural soft daylight, "
         "true-to-life colors, realistic skin texture and natural imperfections, shallow depth of field, "
         "bright clean modern European apartment with white walls, light oak wood and green houseplants. "
         "Cleaners wear a dark forest-green apron over a plain white t-shirt and light green rubber gloves. "
         "No text, no logos, no watermarks, no brand names.")

JOBS = [
    ("hero", "1024x1536", 1000, "A friendly woman cleaner in her late 20s, brown hair in a ponytail, smiling warmly at the camera, holding a cleaning caddy with spray bottles and microfiber cloths, standing in a bright living room with plants and a sofa, waist-up portrait."),
    ("exp-1", "1536x1024", 1100, "A woman cleaner wiping a light wooden coffee table with a blue microfiber cloth in a bright Scandinavian living room, candid moment, seen from the side."),
    ("exp-2", "1024x1024", 700, "A spotless bright living room with a light grey sofa, cushions, a round coffee table, green plants and sunlight through large windows, no people."),
    ("exp-3", "1024x1024", 700, "A woman cleaner cleaning a large window with a squeegee, bright room, green plants on the windowsill, candid."),
    ("s-unterhalt", "1024x1024", 800, "A woman cleaner wiping a white kitchen countertop with a microfiber cloth and spray bottle in a modern bright kitchen, candid."),
    ("s-grund", "1024x1024", 800, "A woman cleaner vacuuming a light carpet next to a grey sofa in a bright living room with plants, full body, candid."),
    ("s-bau", "1024x1024", 800, "A woman cleaner vacuuming dust in a freshly renovated empty apartment with white walls and new light wood floors, a ladder and paint buckets in the background, candid."),
    ("s-fenster", "1024x1024", 800, "A woman cleaner cleaning a tall window pane with a squeegee and spray bottle, sunlight, plants, candid."),
    ("s-buero", "1024x1024", 800, "A male cleaner in his 30s wiping a desk in a bright modern open-plan office with computers and plants, candid."),
    ("s-praxis", "1024x1024", 800, "A woman cleaner disinfecting a reception counter in a bright modern medical practice waiting area, candid."),
    ("s-treppe", "1024x1024", 800, "A male cleaner mopping the stairs of a bright, well-kept apartment building staircase with white walls, candid."),
    ("s-teppich", "1024x1024", 800, "A woman cleaner deep-cleaning a light grey upholstered sofa with a handheld upholstery cleaning machine in a bright living room, candid."),
    ("care", "1024x1024", 900, "A woman cleaner vacuuming the floor with a canister vacuum cleaner beside a light grey sofa in a bright living room with plants, full body, candid, natural."),
    ("offer", "1024x1024", 800, "Studio portrait of a cheerful young woman cleaner with long brown hair, holding a green spray bottle toward the camera and wearing yellow rubber gloves, dark forest-green apron over white t-shirt, against a plain solid deep forest green background (#0f4a2a), even soft lighting, waist-up."),
    ("tips", "1536x1024", 1000, "Still life of eco-friendly cleaning supplies: a wicker basket with plain unlabeled spray bottles, brushes, folded microfiber cloths and a lush green plant, on a white table against a white wall, soft daylight, no people, lots of white space around."),
    ("team", "1536x1024", 1200, "Group photo of a friendly cleaning team of five diverse people (three women, two men, ages 25 to 50) standing together in a bright modern apartment, all wearing dark forest-green aprons over white t-shirts, relaxed genuine smiles, looking at the camera."),
    ("owner", "1024x1536", 900, "Portrait of a confident woman in her mid 40s, founder of a cleaning company, short dark blonde hair, wearing a dark green blouse, arms relaxed, standing in a bright modern office with plants, natural smile."),
    ("avatar-1", "1024x1024", 240, "Close-up headshot of a friendly woman in her 30s with long dark hair, casual sweater, neutral light background, natural smile."),
    ("avatar-2", "1024x1024", 240, "Close-up headshot of a friendly man in his 40s with short hair and light stubble, casual shirt, neutral light background, natural smile."),
    ("avatar-3", "1024x1024", 240, "Close-up headshot of a friendly older woman in her 60s with grey bob haircut and glasses, neutral light background, natural smile."),
]

def gen(job):
    name, size, width, prompt = job
    path = os.path.join(OUT, name + ".jpg")
    if os.path.exists(path) and os.path.getsize(path) > 60000:
        return name, "exists"
    body = json.dumps({"model": "gpt-image-1", "prompt": prompt + " " + STYLE, "size": size,
                       "quality": "high" if not name.startswith("avatar") else "medium", "n": 1}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=body,
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        return name, "ERR " + e.read().decode()[:400]
    img = Image.open(io.BytesIO(base64.b64decode(data["data"][0]["b64_json"]))).convert("RGB")
    h = round(img.height * width / img.width)
    img.resize((width, h), Image.LANCZOS).save(path, "JPEG", quality=84, optimize=True, progressive=True)
    return name, "ok"

only = sys.argv[1:]
jobs = [j for j in JOBS if not only or j[0] in only]
with cf.ThreadPoolExecutor(6) as ex:
    for name, res in ex.map(gen, jobs):
        print(name, res, flush=True)
