
# Demonstration of Order Match Engine

```python
from match_engine import Order, Book, MatchEngine
```

# Building Blocks

## Order


```python
O1 = Order('AAPL', 'bid', 10.2, 10)
# print(O1.time, O1.product, O1.buysell, O1.price, O1.quantity)
print(O1)
O1.update(product='GOOGL', buysell='ask', price=100, quantity=100)
# print(O1.time, O1.product, O1.buysell, O1.price, O1.quantity)
print(O1)
```

    time 1517805088.666956: AAPL, bid, $10.2, 10 shares
    time 1517805088.666956: GOOGL, ask, $100, 100 shares



```python
O1 = Order('AAPL', 'ask', 19.2, 2)
O2 = Order('AAPL', 'bid', 20.2, 10)
O2.match(O1)
```




    (True, {'price': 19.2, 'time': 1517805089.148843, 'volume': 2}, 8, 0)



## Book


```python
AAPL_ASK = Book('AAPL', 'ask')
order1 = Order('AAPL', 'ask', 90.0, 50)
AAPL_ASK.update(Order('AAPL', 'ask', 90.0, 30))
AAPL_ASK.update(Order('AAPL', 'ask', 90.0, 30))
AAPL_ASK.update(Order('AAPL', 'ask', 110.0, 100))
```


```python
AAPL_ASK.show()
print(AAPL_ASK.min(), AAPL_ASK.max())

```

    > AAPL:
       	 Prices 	 Shares
      ASK	 $90.00 	 30
      ASK	 $90.00 	 30
      ASK	 $110.00 	 100
    90.0 110.0



```python
AAPL_ASK.cancel(order1)
AAPL_ASK.show()
print(AAPL_ASK.min(), AAPL_ASK.max())
```

    > AAPL:
       	 Prices 	 Shares
      ASK	 $90.00 	 30
      ASK	 $90.00 	 30
      ASK	 $110.00 	 100
    90.0 110.0



```python
AAPL_ASK.match(Order('AAPL', 'bid', 120.0, 100))
AAPL_ASK.match(Order('AAPL', 'bid', 110.0, 300))
AAPL_ASK.show()
```

    > AAPL:
       	 Prices 	 Shares



```python
AAPL_ASK.transactions
```




    [{'price': 120.0, 'time': 1517805091.083642, 'volume': 30},
     {'price': 120.0, 'time': 1517805091.083651, 'volume': 30},
     {'price': 120.0, 'time': 1517805091.083659, 'volume': 40},
     {'price': 110.0, 'time': 1517805091.0841548, 'volume': 60}]




```python
AAPL_BID = Book('AAPL', 'bid')
AAPL_BID.update(Order('AAPL', 'bid', 101.0, 50))
AAPL_BID.update(Order('AAPL', 'bid', 101.0, 60))
AAPL_BID.update(Order('AAPL', 'bid', 110.0, 70))
AAPL_BID.update(Order('AAPL', 'bid', 110.0, 80))
```


```python
AAPL_BID.show()
```

    > AAPL:
       	 Prices 	 Shares
      BID	 $110.00 	 70
      BID	 $110.00 	 80
      BID	 $101.00 	 50
      BID	 $101.00 	 60



```python
AAPL_BID.match(Order('AAPL', 'ask', 100, 500))
# AAPL_BID.show()
```




    (True,
     [{'price': 100, 'time': 1517805092.7012212, 'volume': 70},
      {'price': 100, 'time': 1517805092.701231, 'volume': 80},
      {'price': 100, 'time': 1517805092.701241, 'volume': 50},
      {'price': 100, 'time': 1517805092.7012448, 'volume': 60}])




```python
AAPL_BID.transactions
```




    [{'price': 100, 'time': 1517805092.7012212, 'volume': 70},
     {'price': 100, 'time': 1517805092.701231, 'volume': 80},
     {'price': 100, 'time': 1517805092.701241, 'volume': 50},
     {'price': 100, 'time': 1517805092.7012448, 'volume': 60}]



# Match Engine


```python
market = MatchEngine('AAPL')
```


```python
order1 = Order('AAPL', 'ask', 99.0, 50)
market.update(order1)
market.show()
market.cancel(order1)
market.show()
market.update(Order('AAPL', 'ask', 99.0, 50))
market.update(Order('AAPL', 'ask', 99.0, 30))
# market.show()
market.update(Order('AAPL', 'ask', 99.0, 30))
market.update(Order('AAPL', 'ask', 100.0, 60))
# market.show()
market.update(Order('AAPL', 'bid', 101.0, 100))
market.update(Order('AAPL', 'bid', 100.4, 70))
market.update(Order('AAPL', 'bid', 99.5, 20))
# market.show()
```

    > AAPL:
       	 Prices 	 Shares
    > AAPL:
       	 Prices 	 Shares
      ASK	 $99.00 	 50
    > AAPL:
       	 Prices 	 Shares
    > AAPL:
       	 Prices 	 Shares



```python
market.transaction_history['AAPL']
```




    [{'price': 101.0, 'time': 1517805094.454997, 'volume': 50},
     {'price': 101.0, 'time': 1517805094.455009, 'volume': 30},
     {'price': 101.0, 'time': 1517805094.4550169, 'volume': 20},
     {'price': 100.4, 'time': 1517805094.455155, 'volume': 10},
     {'price': 100.4, 'time': 1517805094.455168, 'volume': 60}]




```python
market.show()
```

    > AAPL:
       	 Prices 	 Shares
      BID	 $99.50 	 20
    > AAPL:
       	 Prices 	 Shares

