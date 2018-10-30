def pure_function_memoizer():
    MEMO = {}

    def call(fn, *args):
        key = (fn, *args)
        if key not in MEMO:
            MEMO[key] = fn(*args)
        return MEMO[key]

    return call


def events_from_generators(generators=None):
    if generators is None:
        from spark.spark_generators.models import Generator

        generators = Generator.objects.as_generators()
    memoizer = pure_function_memoizer()

    for generator in generators:
        candidates = memoizer(generator["candidates"])
        for candidate in candidates:
            context = generator["context"](candidate)
            for condition in generator["conditions"]:
                if condition["variable"] not in context:
                    break
                if not condition["test"](context[condition["variable"]]):
                    break
            else:
                yield {
                    "group": generator["group"],
                    "key": "{}_{}".format(generator["group"], candidate.pk),
                    "context": context,
                }
