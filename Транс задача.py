from pulp import *
import time

print("ТРАНСПОРТНАЯ ЗАДАЧА - ВАРИАНТ 22")

# 1. Исходные данные для Варианта 22
# ------------------------------------

# Потребности потребителей (верхняя строка)
demand = [200, 300, 200, 300, 100]  
# Запасы поставщиков (первый столбец)
supply = [100, 200, 300, 400, 400]  

# Матрица тарифов (стоимость перевозок)
cost_matrix = [
    [2, 3, 4, 5, 1],   # Поставщик 1
    [2, 4, 2, 6, 7],   # Поставщик 2
    [6, 5, 4, 5, 4],   # Поставщик 3
    [4, 6, 7, 6, 9],   # Поставщик 4
    [5, 7, 6, 9, 8]    # Поставщик 5
]

# 2. Проверка и вывод данных
print("Дано:")
print(f"Запасы поставщиков: {supply} (сумма = {sum(supply)})")
print(f"Потребности потребителей: {demand} (сумма = {sum(demand)})")

# 3. Балансировка задачи
total_supply = sum(supply)
total_demand = sum(demand)

if total_supply != total_demand:
    print(f"\nЗадача несбалансированная! Разница: {abs(total_supply - total_demand)}")
    if total_supply < total_demand: # Нужен доп. поставщик
        supply.append(total_demand - total_supply)
        cost_matrix.append([0] * len(demand)) # Добавление поставщика с нулевыми тарифами
        print("Добавлен фиктивный поставщик.")
    else: # Нужен доп. потребитель
        demand.append(total_supply - total_demand)
        for row in cost_matrix:
            row.append(0) # Добавляем столбец с нулевыми тарифами
        print("Добавлен фиктивный потребитель.")

m = len(supply) # Количество поставщиков (включая фиктивных)
n = len(demand) # Количество потребителей (включая фиктивных)


print(f"\nРазмерность сбалансированной задачи: {m} поставщиков x {n} потребителей")

# 4. Решение методом PuLP
print("Решение методом PULP...")

start_time = time.time()

# Создание переменных x_i_j (сколько везем из i в j)
variables = []
for i in range(m):
    for j in range(n):
        # Имена переменных будут x_1_1, x_1_2, ...
        variables.append(LpVariable(f"x_{i+1}_{j+1}", lowBound=0, cat='Continuous'))

# Создание задачи (минимизация)
problem = LpProblem("Transport_Problem_Variant_22", LpMinimize)

# Целевая функция (минимизировать общую стоимость)
cost_coeffs = []
for i in range(m):
    for j in range(n):
        cost_coeffs.append(cost_matrix[i][j])

# lpDot - это скалярное произведение (стоимость1*перевозка1 + стоимость2*перевозка2 + ...)
problem += lpDot(cost_coeffs, variables), "Total_Cost" 

# Ограничения по поставщикам
# (сумма всех перевозок от одного поставщика_i = его запасу)
for i in range(m):
    constraint_vars = variables[i*n : (i+1)*n] # Переменные для i-го поставщика
    problem += lpSum(constraint_vars) == supply[i], f"Supply_{i+1}"

# Ограничения по потребителям
# (сумма всех перевозок одному потребителю_j = его потребности)
for j in range(n):
    constraint_vars = [variables[i*n + j] for i in range(m)] # Переменные для j-го потребителя
    problem += lpSum(constraint_vars) == demand[j], f"Demand_{j+1}"


# Решаем задачу
# msg=0 отключает лишние сообщения от решателя
problem.solve(PULP_CBC_CMD(msg=0)) 
pulp_time = time.time() - start_time

# 5. Вывод результатов
print("\n--- ОПТИМАЛЬНЫЙ ПЛАН ПЕРЕВОЗОК ---")

total_cost = 0
for variable in problem.variables():
    # Проверяем только те перевозки, которые не равны нулю
    if variable.varValue > 0.001: 
        # Парсим имя переменной (формат: "x_1_2")
        parts = variable.name.split('_')
        supplier = int(parts[1])  
        consumer = int(parts[2])  
        amount = variable.varValue
        
        # Проверяем, является ли потребитель фиктивным
        is_fictional_consumer = (consumer == n) and (total_supply > total_demand)
        
        if is_fictional_consumer:
             print(f"Поставщик {supplier} -> (Остаток на складе): {amount:.1f} ед.")
        else:
            cost = amount * cost_matrix[supplier-1][consumer-1]
            total_cost += cost
            print(f"Поставщик {supplier} -> Потребитель {consumer}: {amount:.1f} ед. x {cost_matrix[supplier-1][consumer-1]} = {cost:.1f}")


print(f"\nМинимальная стоимость: {total_cost:.1f}")
print(f"Время выполнения: {pulp_time:.4f} сек")