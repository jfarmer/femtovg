#include <stdint.h>
int32_t arclen_bench_run(const char *out_csv, const char *kinds, const char *variants, uint32_t rounds, uint32_t inner, int32_t signposts);
void arclen_set_marker(void (*f)(int32_t begin, const char *name));
