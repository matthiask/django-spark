from spark.models import Event
from spark.spark_generators.models import Generator


CONTEXTS = {}


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

        context = CONTEXTS[g["context"]]
        candidates = memoizer(context["candidates"])
        for candidate in candidates:
            variables = context["variables"](candidate)
            for condition in g["conditions"]:
                if condition["variable"] not in variables:
                    break
                if not condition["test"](variables[condition["variable"]]):
                    break
            else:
                e = context["event"](
                    instance=candidate, generator=g, variables=variables
                )
                if Event.objects.create_if_new(e):
                    yield e
