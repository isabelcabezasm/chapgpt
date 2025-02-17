# ChapGPT

ChapGPT is the bot that I use to manage my cap (bottle caps, or crown caps) collection.
It's called "Chap" because cap is "chapa" in Spanish, but you also can see it named as `CapGPT` if I explain this in English, to keep the word game. 

The end goal fo this bot is let you know if I have the cap in my collection or not.

So far, the bot is able to find a cap in an image uploaded by the user and search similar caps in a database.

For the first feature, find a cap in an image, I finetunned the object detector model `YOLO v5`.
ref: https://github.com/ultralytics/yolov5
ref: https://pytorch.org/hub/ultralytics_yolov5/

I used this model based in the [YoloV5 blood cells](https://github.com/sierprinsky/YoloV5_blood_cells) repository, where proves that the algorithm is very good finding the blood cells (that are similar to caps) in an image. 

The bot tries to find the cap in the image and asks to the user if that is the cap that wants to check. 
If not, the user can readjust the detection.

With the image cropped, it search a similar image in CosmosDB. Using a [Vector Search](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search) for NoSQL, is comparing the embeddings of the images with the `DiskANN` vector indexing method and `cosine` distance.

