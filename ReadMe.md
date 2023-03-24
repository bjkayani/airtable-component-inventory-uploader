# Airtable Component Inventory Uploader

This project is used to automatically upload electronic components to my Airtable component inventory using exported CSV of my order from Digikey or LCSC. 

## Airtable Inventory

<img src="images/Screenshot%202023-03-23%20182859.png" alt="Airtable Inventory Screenshot" width="800" height="400">

This is what my Airtable component inventory looks like. I mainly use it to store information about all my electronic components that are used on circuit boards. You can browse around using [this link](https://airtable.com/shr21ZMnu0kvK3dMV).

## Scripts

The scripts in this repo take the BOM exported from LCSC or Digikey, get more information about each component by scrapping information from their product page and then upload this information to Airtable. 

The scripts are heavily dependant on the contents of the BOMs that are loaded into it and the structure of the Airtable inventory database. 

That being said, when it works, it works really well to get as much information about each components and populate that into Airtable without any intervention. 

## Running

- You will need two API keys, Airtable and ImgBB. You can make accounts, get the keys and place them in a file called `config.py`. For Airtable, you will need to create a similar table as mine and get its key as well which you can find in its URL. 
- Download the BOM from either LCSC or Digikey. For both of them, you can simply add components to your cart and export the BOM as a CSV. 
- Depending on which distributor you chose, run the file `<distributor>_airtable_importer.py`.
- If you saved your BOM in `bom` folder, you will be presented that as an option to run. Either select that or enter the full or relative path to your exported BOM. 
- The script will parse the BOM and open an instance of Chrome to start scrapping information from the product pages. 
- Once it has scrapped all the information, it will save the processed BOM in the `bom` folder. It will then continue to try to upload the information to Airtable.
- If all goes well, you should magically see all your components show up in Airtable. 

## Notes

There is a lot that is happening under the hood that could break or be further improved. 

For example, the information scrapped from the websites use Selenium and XCodes of certain elements. If the web design changes or some product page is special for some reason, the script will break.

Another thing that was tricky was getting the right category and footprint since there is no standard way that information is displayed. And since the fields in Airtable are specified by a certain name, the data being set had to be that name. For that, I use a look up table and compare the strings with the list in the table to try to find the closest match. But that doesnt always work and has weaknesses that could be improved in the future. 

## Future Work

- [ ] Combine the scripts and unify duplicate code to allow for one script to provide the complete flow.
- [ ] Add a graphical user interface to interact with the script, upload BOMs, view errors etc.
- [ ] Make the scripts more robust and make the errors more verbose.

