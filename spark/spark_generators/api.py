from spark.models import Event
from spark.spark_generators.models import Generator


SOURCES = {}


def pure_function_memoizer():
    MEMO = {}

    def call(fn, *args):
        key = (fn, *args)
        if key not in MEMO:
            MEMO[key] = fn(*args)
        return MEMO[key]

    return call


def events_from_generators(queryset=None):
    queryset = Generator.objects.all() if queryset is None else queryset
    memoizer = pure_function_memoizer()

    for generator in queryset.prefetch_related("conditions"):
        g = generator.as_generator()

        source = SOURCES[g["source"]]
        candidates = memoizer(source["candidates"])
        for candidate in candidates:
            variables = source["variables"](candidate)
            for condition in g["conditions"]:
                if condition["variable"] not in variables:
                    break
                if not condition["test"](variables[condition["variable"]]):
                    break
            else:
                e = source["event"](
                    instance=candidate, generator=g, variables=variables
                )
                if Event.objects.create_if_new(e):
                    yield e
