# FFF Germany app api to atom feed converter

This script converts data pulled from https://app.fffutu.re/api/v1 and https://app.fffutu.re/ghost/api/v3 to multiple Atom feeds.

## Interface

The script takes one arqument, which is the path that the generated atom files shoulp be put in. Default: `./fff-feeds/`
The data is stored into `.atom` files with each file containing the feed of one OG.

## PSA

The API Token for the **public** API is: bdcdb2d50a3077e0543c0da764
