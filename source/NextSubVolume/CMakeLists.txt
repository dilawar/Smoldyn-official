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
target_link_libraries(nsv PRIVATE CONAN_PKG::eigen CONAN_PKG::boost)

set_property(TARGET nsv PROPERTY POSITION_INDEPENDENT_CODE ON)
