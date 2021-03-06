# Brick Parser
_parser for Brick Lang_

## Definition
Brick is an attempt to create a domain specific modelling language for 
defining house architecture.

## Status
Early prototype.

## High level plan
See https://github.com/alexykot/brick-lang-poc/blob/master/README.md

## Parser design

### Interface 
- designed as a library, but with a set of `tasks` for running 
independently
- basic CLI interface to run parser, provide starting file as 
positional argument
- CLI parser run should load all files, validate, create and cache 
full tree of project files
 
### Process
- ~~grab starting file~~
- ~~recursively traverse all imports and build a single megaobject~~
- ~~normalise all metric values~~ 
- ~~save references to all binary files and check if they exist~~
- ~~output all missing imports or broken references~~

### Limitations
- we are not worried about performance in the PoC
- we are not worried about architecture in the PoC
(megaobject will have to go later)
- we are not doing any structure validations in the PoC
- we only load from local storage, no external dependencies yet
- 3D models contents is not validated, only file presence checked

## Next steps
- ~~prepare parser prototype development~~
- ~~define tasks and goals of the parser~~
- use basic STL example and figure out how to work with it in Python
- create pipeline for web rendering of STL models
- create STLs for all _hello house_ parts
- import all STLs together
- create overall frame model using default settings
- render full frame
- create a way to render parameter controls
- allow to adjust parameters
- create basic intersection checks
