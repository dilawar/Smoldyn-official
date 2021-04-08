
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_CURRENT_BINARY_DIR})

conan_cmake_configure(REQUIRES 
        eigen/3.3.9
        boost/1.75.0
    GENERATORS cmake_find_package
    OPTIONS boost:header_only=True)

conan_cmake_autodetect(settings)

conan_cmake_install(PATH_OR_REFERENCE .
    BUILD missing
    REMOTE conan-center
    SETTINGS ${settings})

find_package(Eigen3 REQUIRED)
find_package(Boost REQUIRED)

if (OPTION_MINGW)
    find_path(SIGNAL_H_DIR signal.h PATHS ${MINGWDIR}/include NO_DEFAULT_PATH)
    if (SIGNAL_H_DIR)
        message(STATUS "signal.h found: '${SIGNAL_H_DIR}'")
    else ()
        message(FATAL_ERROR "signal.h not found")
    endif ()
    include_directories(${SIGNAL_H_DIR})
endif ()

set(SRC_FILES
    StructuredGrid.cpp
    Species.cpp
    ReactionEquation.cpp
    NextSubvolumeMethod.cpp
    Kairos.cpp
    Io.cpp
    Geometry.cpp
    nsvc.cpp)

add_library(nsv STATIC ${SRC_FILES})
target_link_libraries(nsv PRIVATE Eigen3::Eigen Boost::boost)

set_property(TARGET nsv PROPERTY POSITION_INDEPENDENT_CODE ON)
