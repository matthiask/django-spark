from spark.spark_generators.models import Generator


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

        candidates = memoizer(g["candidates"])
        for candidate in candidates:
            context = g["context"](candidate)
            for condition in g["conditions"]:
                if condition["variable"] not in context:
                    break
                if not condition["test"](context[condition["variable"]]):
                    break
            else:
                e = {
                    "group": g["group"],
                    "key": "{}_{}".format(g["group"], candidate.pk),
                    "context": context,
                }
                yield e
