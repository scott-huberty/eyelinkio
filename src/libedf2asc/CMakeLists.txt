cmake_minimum_required(VERSION 3.14)
project(libedf2asc LANGUAGES C CXX)

# Compiler settings
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -DNDEBUG -fPIC")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -DNDEBUG -fPIC")

# Include directory for EyeLink headers
include_directories(${CMAKE_SOURCE_DIR}/include)

# Specify source files
set(SOURCES
    printevent.c
    printrecordinginfo.c
    printsample.c
    main.c
)

# Compile each source file into object files
add_library(printevent_obj OBJECT printevent.c)
add_library(printrecordinginfo_obj OBJECT printrecordinginfo.c)
add_library(printsample_obj OBJECT printsample.c)
add_library(main_obj OBJECT main.c)

# Create a shared library (libedf2asc.so) from the object files
add_library(edf2asc SHARED
    $<TARGET_OBJECTS:printevent_obj>
    $<TARGET_OBJECTS:printrecordinginfo_obj>
    $<TARGET_OBJECTS:printsample_obj>
    $<TARGET_OBJECTS:main_obj>
)

# Link dependencies
target_link_directories(edf2asc PRIVATE /eyelinkio/src/libedfapi/linux/)
target_link_libraries(edf2asc PRIVATE edfapi m z)

# Set the runtime path (RPATH) for the shared library
set_target_properties(edf2asc PROPERTIES
    INSTALL_RPATH /eyelinkio/src/libedfapi/linux/
)
