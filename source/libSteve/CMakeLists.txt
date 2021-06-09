set(
  SRC_FILES
  Geometry.c
  List.c
  math2.c
  opengl2.c
  parse.c
  queue.c
  random2.c
  Rn.c
  RnSort.c
  rxnparam.c
  SimCommand.c
  Sphere.c
  string2.c
  SurfaceParam.c
  Zn.c
  SFMT/SFMT.c
)

add_library(Steve OBJECT ${SRC_FILES})
set_target_properties(Steve PROPERTIES POSITION_INDEPENDENT_CODE ON)

target_include_directories(
  Steve PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/../Smoldyn
  ${CMAKE_BINARY_DIR}
  ${CMAKE_CURRENT_SOURCE_DIR}
)

set_target_properties(Steve PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_compile_options(Steve PUBLIC -Wno-unused-parameter -Wno-unused-function)

if(OPTION_USE_OPENGL)
  find_package(glfw3 REQUIRED)
  find_package(glad REQUIRED)
  target_link_libraries(Steve PRIVATE glfw::glfw glad::glad)
endif(OPTION_USE_OPENGL)

if(OPTION_USE_LIBTIFF)
  list(APPEND DEP_LIBS ${TIFF_LIBRARY})
endif(OPTION_USE_LIBTIFF)
