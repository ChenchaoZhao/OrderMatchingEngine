import numpy as np
import time
import uuid

# Order

class Order:
    """
    O1 = Order('AAPL', 'bid', 10.2, 10)
    # print(O1.time, O1.product, O1.buysell, O1.price, O1.quantity)
    print(O1)
    O1.update(product='GOOGL', buysell='ask', price=100, quantity=100)
    # print(O1.time, O1.product, O1.buysell, O1.price, O1.quantity)
    print(O1)
    
    """
    
    def __init__(self, product, buysell, price, quantity):
        
        self.product = product
        self.time = time.time()
        self.id = uuid.uuid4()
        
        if price > 0:
            self.price = price
        else:
            raise ValueError('price cannot be negative.')
            
        
        if isinstance(quantity, int) and quantity > 0:
            self.quantity = quantity
        else:
            raise ValueError('quantity is a nonnegative integer')
        
        if buysell in ['bid', 'ask']:
            self.buysell = buysell
        else:
            raise ValueError('buysell should be lower case strings "bid" or "ask".')
    
    def update(self, **kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                if key == 'product':
                    self.product = value
                elif key == 'buysell':
                    if value in ['bid', 'ask']:
                        self.buysell = value
                    else:
                        raise ValueError('buysell should be lower case strings "bid" or "ask".')
                elif key == 'price':
                    if value > 0:
                        self.price = value
                    else:
                        raise ValueError('price cannot be negative.')
                elif key == 'quantity':
                    if isinstance(value, int) and value > 0:
                        self.quantity = value
                    else:
                        raise ValueError('quantity is a nonnegative integer')
                else:
                    raise KeyError('No keyword named {}'.format(key))
    def match(self, in_order):
        if isinstance(in_order, Order):
            
            market_data = dict()
            
            if in_order.product is not self.product or in_order.buysell is self.buysell:
                isMatched = False
            else:
                if in_order.buysell is 'bid':
                    isMatched = True if in_order.price >= self.price else False
                elif in_order.buysell is 'ask':
                    isMatched = True if in_order.price <= self.price else False
            
            if isMatched:
                
                market_data['time'] = time.time()
                market_data['volume'] = min(self.quantity, in_order.quantity)
                market_data['price'] = in_order.price
                
                if in_order.quantity >= self.quantity:
                    in_order.quantity -= self.quantity
                    self.quantity = 0
                else:
                    self.quantity -= in_order.quantity
                    in_order.quantity = 0
        else:
            raise TypeError('in_order should be an Order()')
        
        return isMatched, market_data, self.quantity, in_order.quantity
    def __str__(self):
        return 'time {}: {}, {}, ${}, {} shares'.format(self.time, self.product, self.buysell, self.price, self.quantity)
        
# OrderBook

class Book:
    def __init__(self, product, buysell):
        self.product = product
        
        if buysell in ['bid', 'ask']:
            self.buysell = buysell
        else:
            raise ValueError('buysell should be lower case strings "bid" or "ask".')
        
        self.orders_ = dict() # prices as keys, orders as items
        self.n_orders = 0
        self.prices_ = set()
        self.transactions = []
    
    def update(self, new_order):
        if new_order.product is not self.product:
            raise ValueError('>> Order.product {} is inconsistent with Book.product {}.'.format(new_order.product, self.product))
        if new_order.buysell is not self.buysell:
            raise ValueError('>> Order.buysell {} is inconsistent with Book.buysell {}'.format(new_order.buysell, self.buysell))
        
        
        
        if new_order.price in self.prices_:
            self.orders_[new_order.price].append(new_order)
        else:
            self.orders_[new_order.price] = [new_order]
        
        self.prices_.add(new_order.price)
        self.n_orders += 1
        
    def show(self):
        print("> {}:".format(self.product))
        print("   \t Prices \t Shares")
        
        if self.buysell == 'ask':
            is_reversed = False
            marker = 'ASK'
        elif self.buysell == 'bid':
            is_reversed = True
            marker = 'BID'
        
        for price in sorted(self.prices_, reverse=is_reversed):
            for order in self.orders_[price]:
                print("  {}\t ${:3.2f} \t {}".format(marker, round(price, 2), order.quantity))
        
    def match(self, new_order):
        if not isinstance(new_order, Order):
            raise TypeError('in_order should be an Order()')
        if new_order.product is not self.product:
            raise ValueError('>> Order.product {} is inconsistent with Book.product {}.'.format(new_order.product, self.product))
        if new_order.buysell is self.buysell:
            raise ValueError('>> Order.buysell {} should NOT be Book.buysell {}'.format(new_order.buysell, self.buysell))
        
        prices_in_book = sorted(self.prices_) # low to high
        
        isMatched = False
        recent_transactions = []
        
        if new_order.buysell == 'bid' and prices_in_book and prices_in_book[0] <= new_order.price:
            isMatched = True
            idx = len(prices_in_book) - 1
            for price in prices_in_book[::-1]: # from high to low                
                if new_order.price >= price:
                    break
                else:
                    idx -= 1
            matched_prices_ = prices_in_book[:idx+1]
            
            all_done = False
            idx = 0
            while new_order.quantity > 0 and not all_done:
                jdx = 0 # order idx
                to_delete = [] # list of order idx of orders to be deleted after the for loop
                for order in self.orders_[matched_prices_[idx]]:
                    order_match, transaction_data, this_quantity, in_quantity = order.match(new_order)
                    self.transactions.append(transaction_data)
                    recent_transactions.append(transaction_data)
                    
                    if not order_match:
                        raise RuntimeError('Order not matched!')
                    if this_quantity == 0:
                        to_delete.append(jdx)
                        self.n_orders -= 1
                    if in_quantity == 0:
                        break
                    
                    jdx += 1
                
                if len(to_delete) > 0:
                    self.orders_[matched_prices_[idx]][to_delete[0]:to_delete[-1]+1] = []
                if len(to_delete) == jdx+1:
                    del self.orders_[matched_prices_[idx]]
                    self.prices_.remove(matched_prices_[idx])
                
                if idx == len(matched_prices_) - 1:
                    all_done = True
                else:
                    idx += 1
                
        elif new_order.buysell == 'ask' and prices_in_book and prices_in_book[-1] >= new_order.price:
            isMatched = True
            idx = 0
            for price in prices_in_book: # from low to high                
                if new_order.price <= price:
                    break
                else:
                    idx += 1
            matched_prices_ = prices_in_book[idx:]
            matched_prices_ = matched_prices_[::-1] # higher priced offer has priority
                    
            all_done = False
            idx = 0
            while new_order.quantity > 0 and not all_done:
                jdx = 0 # order idx
                to_delete = [] # list of order idx of orders to be deleted after the for loop
#                 print(matched_prices_, matched_prices_[idx])
                for order in self.orders_[matched_prices_[idx]]:
                    order_match, transaction_data, this_quantity, in_quantity = order.match(new_order)
                    self.transactions.append(transaction_data)
                    recent_transactions.append(transaction_data)
                    
                    if not order_match:
                        raise RuntimeError('Order not matched!')
                    if this_quantity == 0:
                        to_delete.append(jdx)
                        self.n_orders -= 1
                    if in_quantity == 0:
                        break
                    
                    jdx += 1
                
                if len(to_delete) > 0:
                    self.orders_[matched_prices_[idx]][to_delete[0]:to_delete[-1]+1] = []
                if len(to_delete) == jdx+1: # if orders of this price are all matched, then remove the key = this_price
                    del self.orders_[matched_prices_[idx]]
                    self.prices_.remove(matched_prices_[idx])
                
                if idx == len(matched_prices_) - 1:
                    all_done = True
                else:
                    idx += 1
        return isMatched, recent_transactions
    
    def __len__(self):
        return self.n_orders
    
    def cancel(self, old_order):
        if not isinstance(old_order, Order):
            raise TypeError('old_order is not an Order()')
        
        if old_order.product != self.product or old_order.buysell != self.buysell:
            raise ValueError('{} is not in this {} Book of {}'.format(old_order.product, self.buysell, self.product))
        else:
            if old_order.price in self.prices_ and old_order in self.orders_[old_order.price]:
                self.orders_[old_order.price].remove(old_order)
                self.n_orders -= 1
    
    def max(self):
        return max(self.prices_)
    def min(self):
        return min(self.prices_)
        
# Match Engine

class MatchEngine:
    def __init__(self, product_list):
        if isinstance(product_list, list):
            """
            e.g. ['AAPL', 'GOOGL', 'C']
            """
            self.product_list = product_list
        elif isinstance(product_list, str):
            """
            e.g. 'AAPL GOOGL C'
            """
            product_list = product_list.split()
            self.product_list = product_list
        
        self.market = dict()
        self.transaction_history = dict()
        for product in self.product_list:
            self.market['{}-bid'.format(product)] = Book(product, 'bid')
            self.market['{}-ask'.format(product)] = Book(product, 'ask')
            self.transaction_history[product] = []
    def __str__(self):
        return ''.join(self.product_list)
    
    def show(self):
        for product in self.product_list:
            self.market['{}-bid'.format(product)].show()
            self.market['{}-ask'.format(product)].show()
    
    def update(self, new_order):
        if not isinstance(new_order, Order):
            raise TypeError('new order is not an Order()')
        
        if new_order.product not in self.product_list:
            raise ValueError('{} of new order is not traded in this market'.format(new_order.product))
        
        if new_order.buysell == 'bid':
            isFilled, recent_transactions = self.market['{}-ask'.format(new_order.product)].match(new_order)
            if isFilled:
                self.transaction_history[new_order.product] += recent_transactions
        elif new_order.buysell == 'ask':
            isFilled, recent_transactions = self.market['{}-bid'.format(new_order.product)].match(new_order)
            if isFilled:
                self.transaction_history[new_order.product] += recent_transactions
                
        if new_order.quantity > 0:
            self.market['{}-{}'.format(new_order.product, new_order.buysell)].update(new_order)
    def cancel(self, old_order):
        if not isinstance(old_order, Order):
            raise TypeError('old order is not an Order()')
        
        if old_order.product not in self.product_list:
            raise ValueError('{} of old order is not traded in this market'.format(new_order.product))
        
        self.market['{}-{}'.format(old_order.product, old_order.buysell)].cancel(old_order)
        
                
             
