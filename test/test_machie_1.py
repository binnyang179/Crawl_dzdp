def get_grad(theta, x, y):
    grad = 2*(theta*x - y)*x
    return -grad


def get_cost(theta, x, y ):
    return (theta*x -y) **2


def gradient_descending(theta, x, y, learning_rate):
    theta = theta + get_grad(theta, x, y)*learning_rate
    return theta


y = 20
x = 1.1

theta = 0
learning_rate = 0.1
cost = get_cost(theta, x, y)
print(cost)
for i in range(30):
    theta = gradient_descending(theta, x, y, learning_rate)
    print(i ,' theta is ',theta)
    cost = get_cost(theta, x, y)
    print(i ,' cost is ',cost)