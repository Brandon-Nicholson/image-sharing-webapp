from dotenv import load_dotenv
from imagekitio import ImageKit
import os

# load environment variables
load_dotenv()

# create imagekit instance
imagekit = ImageKit(
    private_key=os.environ["IMAGEKIT_PRIVATE_KEY"],
    public_key=os.environ["IMAGEKIT_PUBLIC_KEY"],
    url_endpoint=os.environ["IMAGEKIT_URL"],
)