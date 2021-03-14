from random import uniform

data = [uniform(0.0, 20.0) for x in range(1000)]

for dim in [1, 2, 3, 4]:

    dim_cpy = data.copy()
    
    with open(f'random_test_data_{dim}d.txt', 'w') as _file:

        while len(dim_cpy) > 0:
            temp_data = " ".join([str(x) for x in dim_cpy[:dim]])
            _file.write(f"{temp_data}\n")
            dim_cpy = dim_cpy[dim:]

