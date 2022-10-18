from flask import Flask, request
from flask_restful import Resource, Api, abort, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockprediction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Stock Model Class
class StockModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stockName = db.Column(db.String, nullable=False)
    tickerSymbol = db.Column(db.String, nullable=False)
    predictions = db.Column(db.String, nullable=False)

    def __repr__(self):
        return "<Stock(stockName='%s', tickerSymbol='%s', predictions='%s')>" % (
            self.stockName,
            self.tickerSymbol,
            self.predictions
        )

stock_fields = {
    'id': fields.Integer,
    'stockName': fields.String,
    'tickerSymbol': fields.String,
    'predictions': fields.String
}

# Stocks Resource Class
class Stocks(Resource):
    @marshal_with(stock_fields)
    def get(self):
        stocks = StockModel.query.all()
        return stocks

    @marshal_with(stock_fields)
    def post(self):
        data = request.json

        if StockModel.query.filter_by(tickerSymbol=data['tickerSymbol']).first():
            print(data['tickerSymbol'])
            abort(400, message="Stock Already Exists")
        
        stock = StockModel(
            stockName = data['stockName'],
            tickerSymbol = data['tickerSymbol'],
            predictions = data['predictions']
        )

        db.session.add(stock)
        db.session.commit()
        return stock

# Stock Resource Class
class Stock(Resource):
    @marshal_with(stock_fields)
    def get(self, tickerSymbol):
        stock = StockModel.query.filter_by(tickerSymbol=tickerSymbol).first()
        if not stock:
            abort(404, message="That Stock does not exist in your database")
        return stock

    @marshal_with(stock_fields)
    def put(self, tickerSymbol):
        data = request.json
        stock = StockModel.query.filter_by(tickerSymbol=tickerSymbol).first()

        if 'stockName' in data:
            stock.stockName = data['stockName']
        if 'tickerSymbol' in data:
            stock.tickerSymbol = data['tickerSymbol']
        if 'predictions' in data:
            stock.predictions = data['predictions']
        
        db.session.commit()
        return stock, 201

    @marshal_with(stock_fields)
    def delete(self, tickerSymbol):
        stock = StockModel.query.filter_by(tickerSymbol=tickerSymbol).first()
        if not stock:
            abort(404, message="Stock Not Found")
        db.session.delete(stock)
        db.session.commit()

        stock = StockModel.query.all()
        return stock, 204

api.add_resource(Stocks, '/')
api.add_resource(Stock, '/<string:tickerSymbol>')

if __name__ == '__main__':
    app.run()