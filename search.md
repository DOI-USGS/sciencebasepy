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
