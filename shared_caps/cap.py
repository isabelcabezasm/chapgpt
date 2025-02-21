class Cap:
    def __init__(self, id: str, brand_id: int, brand: str, 
                 brand_num: int, type: str | None, brewery: str | None, 
                 region: str | None, country: str, path: str, 
                 embeddings: list | None, base64: str | None) -> None:
        self.id = id                        # cap id
        self.num_reg = int(id)  
        self.brand_id = brand_id            # brand id 
        self.brand = brand                  # brand name  
        self.brand_num = brand_num          # cap #n in that brand 
        self.type = type                    # cap details
        self.brewery = brewery              # productor
        self.region = region                # province or similar
        self.country = country              # cap country
        self.path = path                    # path in db
        self.embeddings = embeddings        # embeddings
        self.base64 = base64                # base64 image

    def to_dict(self):
        return self.__dict__
         
 
