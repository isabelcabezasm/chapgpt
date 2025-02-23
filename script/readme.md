


This simple script, reads all, or some caps identified like a tuple
`(<brand_id>, <cap_num>)` from the storage account, check the details of the cap
in the `.csv` file, build the object cap with the metadata (id, brand_id, brand
name, country, region, etc...), generate the embeddings and save it in the
cosmos db account.

### CSV file

The csv file (check `db/sample.csv`) has this columns (in Spanish):
`N_REG,NUM_MARCA,SUB_NUM,MARCA,TIPO,ESPECIFICA,CERVECERA/PRODUCTOR,PROVINCIA,PAIS,FECHA_OBTE,LUGAR_OBTE`

- **N_REG** is the id of the row
- **NUM_MARCA** brand id
- **SUB_NUM** cap number inside the brand
- **MARCA** brand name
- **TIPO** big one or normal one.
- **ESPECIFICA** some details (txt)
- **CERVECERA/PRODUCTOR** brewering
- **PROVINCIA**  region (for Spanish caps)
- **PAIS** country
- **FECHA_OBTE** date I got it
- **LUGAR_OBTE** place I got it

### Images in the storage account

My storage has a container called `capimagedb` where I have all the images of the caps.
The structure is: folders: `A`, `B`, `C`, `D`.... `W`, `XYZ`, `z SIN MARCA`. 
Inside each character there are one or several folders to group the brands:
`0-AI`, `AK-AN`, `AO-AZ`.
Inside one folder for each brand.
Inside each folder, the image files with a name with this pattern:
`<brand_id>-<cap_num>.jpg`
where the `brand_id` is a number that identifies the brand (parent key for the cap identifier)
and the `cap-num` is the number of the cap for this brand (sub-key or child key).
So the path of each cap image is like (E.g.)   `E/E-EL/Einsiedler/1621-1.jpg`

### Environment variables

The `.env` file is not commited.
Copy `sample.env` as `.env` and fill the needed information.

### Cosmos DB

Only available "clickops":

- Create Cosmos DB for NoSQL
- Enable the feature "Vector Search for NoSQL API" 
- Create a new container. Partition key `/country`, no PK (takes by default /id)
- Container Vector Policy -> path `/embeddings`, type `float32`, distance `cosine`, dimension `2048`and `diskANN` as vector index.

#### Permissions to the cosmos db

ref: https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/tutorial-vm-managed-identities-cosmos?tabs=azure-cli#grant-access

Check the id of the 

```bash
az cosmosdb sql role definition list --account-name <account-name> --resource-group cap_comparer
```

Check the ID of the role with name "Cosmos DB Built-in Data Contributor"
Probably '00000000-0000-0000-0000-000000000002'

The principal id, in my case is the `Object Id` of my user in Entra.

```bash
resourceGroupName='<myResourceGroup>'
accountName='<myCosmosAccount>'
readOnlyRoleDefinitionId='00000000-0000-0000-0000-000000000002' # This is the ID of the Cosmos DB Built-in Data contributor role definition
principalId="1111111-1111-11111-1111-11111111" # This is the object ID of the managed identity.

az cosmosdb sql role assignment create --account-name $accountName --resource-group $resourceGroupName --scope "/" --principal-id $principalId --role-definition-id $readOnlyRoleDefinitionId
```

Result:

```json
{
  "id": "/subscriptions/3fc8226e-ee1e-4b95-a896-aa27789c6cc6/resourceGroups/cap_comparer/providers/Microsoft.DocumentDB/databaseAccounts/cosmosdbforchapgpt/sqlRoleAssignments/12d50ec2-98fa-47e5-8463-e97326c47d89",
  "name": "12d50ec2-98fa-47e5-8463-e97326c47d89",
  "principalId": "d2597c80-39ac-40db-b46b-ba4dfa2acc1b",
  "resourceGroup": "cap_comparer",
  "roleDefinitionId": "/subscriptions/3fc8226e-ee1e-4b95-a896-aa27789c6cc6/resourceGroups/cap_comparer/providers/Microsoft.DocumentDB/databaseAccounts/cosmosdbforchapgpt/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002",
  "scope": "/subscriptions/3fc8226e-ee1e-4b95-a896-aa27789c6cc6/resourceGroups/cap_comparer/providers/Microsoft.DocumentDB/databaseAccounts/cosmosdbforchapgpt",
  "type": "Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments"
}
``` 