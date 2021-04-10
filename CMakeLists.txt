# Main CMakeLists.txt file to build Smoldyn, its libraries, and its utilities using CMake.
# Written by Steve Andrews, April 16, 2012. Updated by Steve Andrews since then.
# This file, and other files of the Smoldyn project, are licensed with LGPL license.
# The primary Smoldyn web site is http://www.smoldyn.org.
# Please report bugs and problems to support@smoldyn.org. 

########## Basic setup ##########
cmake_minimum_required(VERSION 3.12)   # due to better Python support 

project(smoldyn LANGUAGES CXX C)

# CI/CD can also set this variable. If not, use the default one.
if(NOT SMOLDYN_VERSION)
    find_package(Git QUIET)
    if(GIT_FOUND)
        # Is the current commit tagged? If yes, this command will return the
        # tag else it returns empty. If a valid tag is found, then use it for a
        # release.
        execute_process(COMMAND ${GIT_EXECUTABLE} tag --points-at HEAD
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            OUTPUT_VARIABLE SMOLDYN_TAG	
            OUTPUT_STRIP_TRAILING_WHITESPACE)
        if(SMOLDYN_TAG)
            # drop v from the tag to get the version info.
            string(SUBSTRING ${SMOLDYN_TAG} 1 -1 SMOLDYN_VERSION)
            message(STATUS " -- Found a release tag ${SMOLDYN_TAG}")
        else()
            # nightly release / upcoming release preview. 
            # NOTE: Change is appropriately after a release. Can't find a good
            # way to automate this process.
            string(TIMESTAMP STAMP "%Y%m%d")
            set(SMOLDYN_VERSION "2.65.dev${STAMP}")
        endif()
    endif()
endif()
message(STATUS "Smoldyn version set to: '${SMOLDYN_VERSION}'")

# Default build type.
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_STANDARD 14)

######### Targets to build ###########

option(OPTION_TARGET_SMOLDYN "Create stand-alone Smoldyn program" ON)
option(OPTION_TARGET_LIBSMOLDYN "Create LibSmoldyn library" ON)

message(STATUS "Compiling for Smoldyn: ${OPTION_TARGET_SMOLDYN}")
message(STATUS "Compiling for Libsmoldyn: ${OPTION_TARGET_LIBSMOLDYN}")


####### Compiling options ##########

option(OPTION_VCELL "Compile Smoldyn for VCell" OFF)
option(OPTION_MINGW "Cross-compile for Windows using MinGW compiler" OFF)

option(OPTION_NSV "Compile Smoldyn with NextSubvolume functionality" ON)
option(OPTION_VTK "Compile Smoldyn with VTK functionality" OFF)
option(OPTION_STATIC "Compile Smoldyn with static libraries" OFF)
option(OPTION_USE_OPENGL "Build with OpenGL support" ON)
option(OPTION_USE_LIBTIFF "Build with LibTiff support" ON)
option(OPTION_USE_ICONV "Build with Libiconv support" OFF)
option(OPTION_USE_ZLIB "Build with Zlib support" OFF)
option(OPTION_PYTHON  "Build Python module" ON)
option(OPTION_EXAMPLES "Run Libsmoldyn tests" OFF)
option(OPTION_STRICT_BUILD "Treat most warnings as error and enable ASAN" OFF)
option(OPTION_DOCS "Generate documentation" OFF)

if (OPTION_VCELL)
    set(OPTION_USE_LIBTIFF OFF)
    set(OPTION_USE_ZLIB OFF)
    set(HAVE_ZLIB TRUE)
    set(OPTION_USE_ICONV OFF)
    set(HAVE_ICONV FALSE)
endif ()

if (OPTION_STATIC)
#    set(OPTION_USE_ZLIB ON)
endif ()

if (OPTION_PYTHON)
    if(NOT OPTION_TARGET_LIBSMOLDYN)
        set(OPTION_TARGET_LIBSMOLDYN ON)
        message(STATUS "Compiling for Libsmoldyn: ${OPTION_TARGET_LIBSMOLDYN}")
    endif ()
endif ()

message(STATUS "Option to compile Smoldyn for VCell: ${OPTION_VCELL}")
message(STATUS "Option to cross-compile for Windows using MinGW: ${OPTION_MINGW}")
if (OPTION_MINGW)
    message(STATUS "MinGW toolchain file: '${CMAKE_TOOLCHAIN_FILE}'")
endif ()
message(STATUS "Option to include NextSubvolume: ${OPTION_NSV}")
message(STATUS "Option to include VTK: ${OPTION_VTK}")
message(STATUS "Option to compile with static libraries: ${OPTION_STATIC}")
message(STATUS "Option to include OpenGL support: ${OPTION_USE_OPENGL}")
message(STATUS "Option to include LibTiff: ${OPTION_USE_LIBTIFF}")
message(STATUS "Option to include Zlib: ${OPTION_USE_ZLIB}")
message(STATUS "Option to incude Python module: ${OPTION_PYTHON}")
message(STATUS "Option to run Libsmoldyn examples: ${OPTION_EXAMPLES}")
message(STATUS "Option to build documentation: ${OPTION_DOCS}")


#
# conan package manager. 
#
find_package(Python3 COMPONENTS Interpreter REQUIRED)
find_program(CONAN conan HINTS $ENV{HOME}/.local/bin)
if(NOT CONAN)
    message(STATUS "Installing conan using python3-pip")
    execute_process(COMMAND ${Python3_EXECUTABLE} -m pip install conan)
endif()
include(${CMAKE_SOURCE_DIR}/cmake/conan.cmake)

# location of generated cmake modules
list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})

set(CONAN_LIBS "")
set(CONAN_OPTIONS "")
if(OPTION_NSV)
    list(APPEND CONAN_LIBS boost/1.75.0 eigen/3.3.9)
    list(APPEND CONAN_OPTIONS boost:header_only=True)
endif(OPTION_NSV)

if(OPTION_USE_LIBTIFF)
    list(APPEND CONAN_LIBS libtiff/4.2.0)
    list(APPEND CONAN_OPTIONS libtiff:zstd=False 
        libtiff:jbig=False 
        libtiff:webp=False
        libtiff:jpeg=False
        libtiff:libdeflate=False)
endif()

if(OPTION_USE_ZLIB)
    list(APPEND CONAN_LIBS zlib/1.2.11)
endif(OPTION_USE_ZLIB)

if(OPTION_USE_ICONV)
    list(APPEND CONAN_LIBS libiconv/1.16)
endif(OPTION_USE_ICONV)

if(OPTION_USE_OPENGL)
    list(APPEND CONAN_LIBS glfw/3.3.3)
endif()

#
# Install using conan
#
conan_cmake_configure(REQUIRES ${CONAN_LIBS} 
    GENERATORS cmake_find_package
    OPTIONS ${CONAN_OPTIONS})

conan_cmake_autodetect(settings)
conan_cmake_install(PATH_OR_REFERENCE .
    BUILD missing
    REMOTE conan-center
    SETTINGS ${settings})

######### Core code information ###########

set(HEADER_FILES
	${CMAKE_SOURCE_DIR}/source/libSteve/Geometry.h
	${CMAKE_SOURCE_DIR}/source/libSteve/List.h
	${CMAKE_SOURCE_DIR}/source/libSteve/math2.h
	${CMAKE_SOURCE_DIR}/source/libSteve/opengl2.h
	${CMAKE_SOURCE_DIR}/source/libSteve/parse.h
	${CMAKE_SOURCE_DIR}/source/libSteve/queue.h
	${CMAKE_SOURCE_DIR}/source/libSteve/random2.h
	${CMAKE_SOURCE_DIR}/source/libSteve/Rn.h
	${CMAKE_SOURCE_DIR}/source/libSteve/RnSort.h
	${CMAKE_SOURCE_DIR}/source/libSteve/rxnparam.h
	${CMAKE_SOURCE_DIR}/source/libSteve/SimCommand.h
	${CMAKE_SOURCE_DIR}/source/libSteve/Sphere.h
	${CMAKE_SOURCE_DIR}/source/libSteve/string2.h
	${CMAKE_SOURCE_DIR}/source/libSteve/SurfaceParam.h
	${CMAKE_SOURCE_DIR}/source/libSteve/Zn.h
	${CMAKE_SOURCE_DIR}/source/libSteve/SFMT/SFMT.h
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smoldyn.h
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smoldynfuncs.h
	${CMAKE_SOURCE_DIR}/source/vcell/SimpleMesh.h
	${CMAKE_SOURCE_DIR}/source/vcell/SimpleValueProvider.h
	${CMAKE_SOURCE_DIR}/source/NextSubVolume/nsvc.h
	${CMAKE_SOURCE_DIR}/source/vtk/vtkwrapper.h
	)

set(SRC_FILES
	${CMAKE_SOURCE_DIR}/source/libSteve/Geometry.c
	${CMAKE_SOURCE_DIR}/source/libSteve/List.c
	${CMAKE_SOURCE_DIR}/source/libSteve/math2.c
	${CMAKE_SOURCE_DIR}/source/libSteve/opengl2.c
	${CMAKE_SOURCE_DIR}/source/libSteve/parse.c
	${CMAKE_SOURCE_DIR}/source/libSteve/queue.c
	${CMAKE_SOURCE_DIR}/source/libSteve/random2.c
	${CMAKE_SOURCE_DIR}/source/libSteve/Rn.c
	${CMAKE_SOURCE_DIR}/source/libSteve/RnSort.c
	${CMAKE_SOURCE_DIR}/source/libSteve/rxnparam.c
	${CMAKE_SOURCE_DIR}/source/libSteve/SimCommand.c
	${CMAKE_SOURCE_DIR}/source/libSteve/Sphere.c
	${CMAKE_SOURCE_DIR}/source/libSteve/string2.c
	${CMAKE_SOURCE_DIR}/source/libSteve/SurfaceParam.c
	${CMAKE_SOURCE_DIR}/source/libSteve/Zn.c
	${CMAKE_SOURCE_DIR}/source/libSteve/SFMT/SFMT.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolbng.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolboxes.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolcmd.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolcomparts.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolfilament.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolgraphics.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolmolec.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolport.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smollattice.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolreact.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolrule.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolsim.cpp
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolsurface.c
	${CMAKE_SOURCE_DIR}/source/Smoldyn/smolwall.c
	)

set(MAIN_FILES ${CMAKE_SOURCE_DIR}/source/Smoldyn/smoldyn.cpp)

include_directories(source/libSteve source/Smoldyn ${CMAKE_BINARY_DIR})

if(OPTION_VCELL)
    list(APPEND SRC_FILES
        source/Smoldyn/smoldynhybrid.c
        source/vcell/SimpleMesh.cpp
        source/vcell/SimpleValueProvider.cpp )
    include_directories(source/vcell)
endif(OPTION_VCELL)

if(OPTION_TARGET_LIBSMOLDYN)
    list(APPEND HEADER_FILES ${CMAKE_SOURCE_DIR}/source/Smoldyn/libsmoldyn.h)
    list(APPEND SRC_FILES ${CMAKE_SOURCE_DIR}/source/Smoldyn/libsmoldyn.cpp)
endif(OPTION_TARGET_LIBSMOLDYN)

if(OPTION_USE_LIBTIFF AND NOT OPTION_USE_OPENGL)
    message(WARNING "LibTiff won't be used because build does not include OpenGL.")
    set(OPTION_USE_LIBTIFF OFF)
endif()

set_source_files_properties(${SRC_FILES} PROPERTIES LANGUAGE CXX )
set_source_files_properties(${MAIN_FILES} PROPERTIES LANGUAGE CXX )


####### Compiler flags ######################

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING
        "Choose the buid type: None, Debug, Release, RelWithDebInfo, or MinSizeRel" FORCE)
endif ()

if(OPTION_STRICT_BUILD)
    add_definitions(-Wall -Werror)
    # add_definitions(-Wno-format-truncation)
    # See https://stackoverflow.com/a/14132910/1805129
    add_definitions(-Wno-uninitialized)
    # Address sanitizer
    set(CMAKE_BUILD_TYPE Debug)
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address")
    set(CMAKE_LINKER_FLAGS_DEBUG "${CMAKE_LINKER_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address")
endif()

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

set(VCELL_BUILD OFF)
set(APPLE_BUILD OFF)
set(NIX_BUILD OFF)
set(MINGW_BUILD OFF)
set(WINDOWS_BUILD OFF)

if (OPTION_VCELL)
    set(VCELL_BUILD ON)
    message(STATUS "Compiling for VCell")
    add_compile_options(-D_CRT_SECURE_NO_WARNINGS)
    link_directories(${CMAKE_CURRENT_SOURCE_DIR}/source/vcell)
elseif (OPTION_MINGW)
    set(MINGW_BUILD ON)
    message(STATUS "Cross-compiling for Windows using MinGW libraries from: ${MINGWDIR}")
    set(BNG2_PATH "%PROGRAMFILES%\\\\Smoldyn\\\\BioNetGen\\\\BNG2.pl")
    include_directories(${MINGWDIR}/include)
    link_directories(${MINGWDIR}/lib)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D FREEGLUT_STATIC -static")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D FREEGLUT_STATIC -static")
    set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "${CMAKE_SHARED_LIBRARY_LINK_C_FLAGS} -static -s")
    set(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "${CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS} -static -s")
elseif (APPLE)
    set(APPLE_BUILD ON)
    message(STATUS "Compiling on an Apple computer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wno-deprecated -mmacosx-version-min=10.9")
    set(BNG2_PATH "/usr/local/bin/BioNetGen/BNG2.pl")
elseif (WIN32)
    set(WINDOWS_BUILD ON)
    if(MSVC)
        add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    endif()

    message(STATUS "Compiling on a Windows computer")
    set(BNG2_PATH "%PROGRAMFILES%\\\\Smoldyn\\\\BioNetGen\\\\BNG2.pl")
    if (OPTION_VTK)
        message(WARNING "VTK not included because it isn't supported for Windows build")
        set(OPTION_VTK OFF)
    endif ()
else ()
    set(NIX_BUILD ON)
    message(STATUS "Compiling on a Linux computer")
    set(BNG2_PATH "/usr/local/bin/BioNetGen/BNG2.pl")
endif ()

message(STATUS "CMAKE_CXX_FLAGS variable: '${CMAKE_CXX_FLAGS}'")
message(STATUS "BioNetGen path: '${BNG2_PATH}' ")


####### Option: Build with OpenGL (gl and glu only, not glut) ##########
if (OPTION_USE_OPENGL)
    # see cmake --help-policy CMP0072"
    set(HAVE_OPENGL TRUE)
    find_package(glfw3 REQUIRED)
    list(APPEND DEP_LIBS glfw::glfw)
endif()


####### Build with LibX11 (only required for static build on Mac) ##########

#if (OPTION_STATIC AND OPTION_USE_OPENGL AND HAVE_OPENGL)
#	   find_package(X11)
#	   if (X11_FOUND)
#        message(STATUS "Found X11: '${X11_INCLUDE_DIR}', '${X11_LIBRARIES}'")
#    else ()
#        message(FATAL_ERROR "X11 not found")
#    endif ()
#    include_directories(${X11_INCLUDE_DIR})
#    list(APPEND DEP_LIBS ${X11_LIBRARIES})
#endif()


####### Option: Build with LibTiff ##########

if (OPTION_USE_LIBTIFF)
    find_package(TIFF REQUIRED)
    list(APPEND DEP_LIBS TIFF::TIFF)
endif ()


####### Option: Build with Zlib ##########

if(OPTION_USE_ZLIB)
    find_path(ZLIB REQUIRED)
    include_directories(${ZLIB_INCLUDE_DIRS})
    list(APPEND DEP_LIBS ${ZLIB_LIBRARIES})
endif(OPTION_USE_ZLIB)


####### Option: Build with iconv ##########

if(OPTION_USE_ICONV)
    find_pacakge(Iconv REQUIRED)
    include_directories(${Iconv_INCLUDE_DIRS})
    list(APPEND DEP_LIBS Iconv::Iconv)
endif(OPTION_USE_ICONV)


####### Option: Build with VTK ##########

if(OPTION_VTK)
    add_definitions(-DHAVE_VTK)
    find_package(VTK REQUIRED)
    include_directories(source/vtk ${VTK_INCLUDE_DIRS})
    list(APPEND SRC_FILES source/vtk/vtkwrapper.cpp)
    list(APPEND HEADER_FILES source/vtk/vtkwrapper.h)
    list(APPEND DEP_LIBS ${VTK_LIBRARIES})
endif(OPTION_VTK)


####### Option: Build with NextSubvolume ##########

if (OPTION_NSV)
    add_subdirectory(source/NextSubVolume)
    include_directories(source/NextSubVolume)
    list(APPEND DEP_LIBS nsv)
endif (OPTION_NSV)


####### Targets ##########

if (OPTION_TARGET_SMOLDYN)
    add_executable(smoldyn ${SRC_FILES} ${MAIN_FILES} ${HEADER_FILES})
    target_link_libraries(smoldyn PRIVATE ${DEP_LIBS})
endif ()

if (OPTION_TARGET_LIBSMOLDYN)
    add_library(smoldyn_shared SHARED ${SRC_FILES} ${HEADER_FILES})
    add_library(smoldyn_static STATIC ${SRC_FILES} ${HEADER_FILES})
    set_property(TARGET smoldyn_static PROPERTY POSITION_INDEPENDENT_CODE ON)
    target_link_libraries(smoldyn_shared ${DEP_LIBS})
    target_link_libraries(smoldyn_static ${DEP_LIBS})
    if (APPLE_BUILD)
        set_target_properties(smoldyn_shared PROPERTIES LINK_FLAGS "-framework Glut -framework OpenGL")
    elseif (WINDOWS_BUILD)
        set_target_properties(smoldyn_shared PROPERTIES PREFIX "lib")
        set_target_properties(smoldyn_static PROPERTIES PREFIX "lib")
    endif ()
endif ()


########## Python module #########

if (OPTION_PYTHON)
    add_subdirectory(${CMAKE_SOURCE_DIR}/source/python)
endif ()


########## install ###########

if(NOT OPTION_MINGW)

    if (OPTION_TARGET_SMOLDYN)
        install(TARGETS smoldyn RUNTIME DESTINATION bin)
    endif()

    if (OPTION_TARGET_LIBSMOLDYN)
        install(TARGETS smoldyn_shared LIBRARY DESTINATION lib)
        install(TARGETS smoldyn_static ARCHIVE DESTINATION lib)
        install(FILES source/Smoldyn/libsmoldyn.h source/Smoldyn/smoldyn.h
            ${CMAKE_CURRENT_BINARY_DIR}/smoldynconfigure.h
            DESTINATION include)
    endif ()
endif ()


########## configure file #########
configure_file (
    ${CMAKE_CURRENT_SOURCE_DIR}/source/smoldynconfigure.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/smoldynconfigure.h
    )

######### docs ##############
if(OPTION_DOCS)
    add_subdirectory(docs)
endif(OPTION_DOCS)

########## package #########
include(CPack)


######### Testing #############
enable_testing()
if (OPTION_TARGET_LIBSMOLDYN AND OPTION_EXAMPLES)
    add_subdirectory(examples)
endif ()

