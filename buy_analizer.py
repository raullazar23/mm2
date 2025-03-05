

def buy_analizer(data):
    """
    Function to analyze the data and return the result
    :param data: list of dictionaries
    :return: list of dictionaries
    """
    result = []
    for item in data:
        if item['price'] > 100:
            item['status'] = 'expensive'
        else:
            item['status'] = 'cheap'
        result.append(item)
    return result