# wcofun-dl
quick and simple downloader for my favorite anime/cartoon site
uses headless chrome and selenium cause the site uses some javascript based drm that I am too lazy to reverse engineer.
also just throws the link at curl cause I am too lazy to translate that into requests.
developed and tested on Linux. On windows it should work if you install the proper curl app I think.

## basic usage
`-l link` give it the link to the episode list. it will scrape the individual episode links. default names will be "<episode number> - <everything before the word 'episode'>"
`-s file` will save names and video-file links in a text file which allows you to edit the file names if you want
`-o dir` choose the output directory. '.' by default
`-f file` will read in from a file created by the -s option and use that info to download the episodes. this step will not use selenium