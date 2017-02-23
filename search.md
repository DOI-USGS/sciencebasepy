q = simple text search

## Children
parentId — find all items that have the given ID as its parentID, or in its linked parent IDs
ancestors — find all ancestors of the item specified by the given ID
ancestors=50461941e4b0241d49d62bab


browseType
browseCategory
itemTypes
party
itemIdentifier
searchExtent

facets

## Filters
filter=<filter>

ancestors
dateRange={“choice”: ?, “start”: ?, “end”: ?, “dateType”: ?}
dateRange={“dateType”:"End", "choice":"year"}
tags=water
tags={"name":name, "type":type, "scheme":scheme}
spatialQuery
extentQuery

## Conjunction
filter=tags=water&filter=tags=birds&conjunction=tags=OR

## Lucene Search
lq = lucene query on the Item JSON model

## Sorting and Paging Results
sort — sort by title, dateCreated, lastUpdated, or firstContact
max
offset

## Specifying Result Fields
fields
fieldset

## Faceted Searching
enableFacets
facetSize
facetTagTypes (csv or multiparam)
facetTagSchemes csv or multiparam)

## Item Identifier
itemIdentifier={“type”: <type>, “key”: <key>}


## Stuff
format=json
This of course tells ScienceBase to return the results in JSON.
 
The remaining parameters I'll split into two sections.  The first section controls what is returned in the "items" section of the JSON. 

q=
This is a keyword search.  All searches should contain this, and if there are no keywords (as in this case), the value is left blank.
 
filter0=ancestors=56d4d719e4b056577c3e1f1f
ScienceBase lets you add multiple filters, filter0, filter1, filter2 etc.  This filter is an "ancestors" search, which returns all descendants of the item with the given ID.  The parent AXL item is at https://beta.sciencebase.gov/catalog/item/56d4d719e4b056577c3e1f1f, so this is asking for every item under that item.

fields=title,summary,distributionLinks,webLinks,previewImage
This tells ScienceBase to add the title, summary, distributionLinks, webLinks and previewImage sections to the JSON for each item that matches the query. 

max=20
Return at most 20 items.
 
offset=20
Start at the 21st item in the results.  Consequently, in this case since there are only 17 items that match the criteria, the query will not return any items. 

The remaining request parameters have to do with the searchFacets section of the JSON.  These are the elasticsearch groups that you see displayed on the left hand side of the AXL Test Collection prototype.  This allows the application to display how many items meet certain search criteria, which is how, for example, the app shows that there are nine items tagged as Order "trichoptera."

facets=browseCategory,browseType,partyWithName,tagType,tagScheme,tagNameForTypeAndScheme,tagNameForTypes
This tells ScienceBase which facet information to send about the search results.  Looking at the JSON, I believe that the app is only using tagNameForTypes.

facetTagTypes=Order,Family,Taxon
Since we are requesting search facet information about tagNameForTypes, this tells ScienceBase which types we are interested in.
 
facetSize=30 
This is the limit of the number of entries in each search facet.  For example, say that we had hundreds of Taxons in the system.  So, these three parameters together say, "Give me tagNameForTypes facets.  The tag types I care about are Order, Family and Taxon.  And I only want the first 30 of each type."

## More Stuff
50461941e4b0241d49d62bab

https://beta.sciencebase.gov/catalog/items?q=&filter=ancestors=50461941e4b0241d49d62bab

https://beta.sciencebase.gov/catalog/items?q=&lq=(tags.name(+birds)%20AND%20tags.name(+water))%20OR%20tags.name(+WY)

https://beta.sciencebase.gov/catalog/items?q=&lq=(title%3A%22Happy+Project%22%20AND%20body:%22This%22)&format=json&fields=title,body,tags

https://www.sciencebase.gov/catalog/items?filter0=facets.facetName%3DBASIS+Plus&filter1=browseType%3DBASIS%2B+Task&filter2=partyWithName%3D17368_FT+COLLINS+SCI+CTR&filter3=dateRange%3D%7B%22start%22%3A%222014-03-04%22%2C%22end%22%3A%222020-03-04%22%2C%22dateType%22%3A%22End+Date%22%7D

https://www.sciencebase.gov/catalog/items?s=Search&q=water&fields=title,summary,body&facets=browseCategory&format=json

q = simple text search

lq = lucene query on the Item JSON model
ancestors — find all ancestors of the item specified by the given ID
parentId — find all children of the item specified by the given ID, including linked parent IDs
tags
q=&filter=tags=water

browseType
browseCategory
itemTypes
party
itemIdentifier
searchExtent
mq
mqIdentifier — mongo identifier search
max
offset
facets
facetTagTypes (csv or multiparam)
facetTagSchemes csv or multiparam)
facetSize
mode = quick
fields
fieldset
enableFacets
searchExtent
sort — sort by title, dateCreated, lastUpdated, or firstContact

filter=dateRange={“choice”: ?, “start”: ?, “end”: ?, “dateType”: ?}
filter1=tags={"type":"sampletype","name":"thin section"}&filter2=tags={"type":"nnss","name":"nnss_area05"}