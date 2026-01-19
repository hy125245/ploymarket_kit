TRADES_QUERY = """
query Trades($limit: Int, $offset: Int) {
  trades(limit: $limit, offset: $offset) {
    id
    marketId
    userId
    side
    price
    size
    createdAt
    profit
    realized
  }
}
"""

MARKETS_QUERY = """
query Markets($limit: Int, $offset: Int) {
  markets(limit: $limit, offset: $offset) {
    id
    question
    volume24h
    volume
    status
    createdAt
  }
}
"""

USERS_QUERY = """
query Users($limit: Int, $offset: Int) {
  users(limit: $limit, offset: $offset) {
    id
    address
  }
}
"""
