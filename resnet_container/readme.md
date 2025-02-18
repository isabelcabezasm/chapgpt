# ResNet Container

This container contains the API that:

1. uses the finetunned YOLOv5 model for finding a cap in an image
1. generates the embeddings of the cap images  with ResNet50 

The API is build with FastAPI and it doesn't have authentication, but the
container in Azure Container App only can be called from the frontend.

The main file is the entry point. It contains two endpoints: `find_cap` and  `embed`.
Both accept a `File` and return a list of decimals.

The `find_cap` method returns four floats: the points that define the square
where the cap is in the image. The model can find more than one cap, but
currently is only returning the object with more posibilities "to be a cap".
If it doesn't find any cap, it will return an empty list.

The `embed` method returns a list of 2048 floats: the embeddings of the image. 


## Local run

You can test the container with something like this:

```bash
curl -F "file=@./cap1.jpeg" http://embeddings:8080/embed
```
