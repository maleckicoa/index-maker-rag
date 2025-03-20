
industries = """Industries in the Basic Materials sector are : Agricultural Inputs, Aluminum, Chemicals, Chemicals - Specialty, Construction Materials, Copper, Gold, Industrial Materials, Other Precious Metals, Paper, Lumber & Forest Products, Silver, Steel
Industries in the Communication Services sector are : Advertising Agencies, Broadcasting, Entertainment, Internet Content & Information, Publishing, Telecommunications Services
Industries in the Consumer Cyclical sector are : Apparel - Footwear & Accessories, Apparel - Manufacturers, Apparel - Retail, Auto - Dealerships, Auto - Manufacturers, Auto - Parts, Auto - Recreational Vehicles, Consumer Cyclical, Department Stores, Furnishings, Fixtures & Appliances, Gambling, Resorts & Casinos, Home Improvement, Leisure, Luxury Goods, Packaging & Containers, Personal Products & Services, Residential Construction, Restaurants, Specialty Retail, Travel Lodging, Travel Services
Industries in the Consumer Defensive sector are : Agricultural Farm Products, Beverages - Alcoholic, Beverages - Non-Alcoholic, Beverages - Wineries & Distilleries, Discount Stores, Education & Training Services, Food Confectioners, Food Distribution, Grocery Stores, Household & Personal Products, Packaged Foods, Tobacco
Industries in the Energy sector are: Coal, Oil & Gas Drilling, Oil & Gas Equipment & Services, Oil & Gas Exploration & Production, Oil & Gas Integrated, Oil & Gas Midstream, Oil & Gas Refining & Marketing, Solar, Uranium
Industries in the Financial Services sector are: Asset Management, Asset Management - Bonds, Asset Management - Global, Asset Management - Income, Asset Management - Leveraged, Banks - Diversified, Banks - Regional, Financial - Capital Markets, Financial - Conglomerates, Financial - Credit Services, Financial - Data & Stock Exchanges, Financial - Diversified, Financial - Mortgages, Insurance - Brokers, Insurance - Diversified, Insurance - Life, Insurance - Property & Casualty, Insurance - Reinsurance, Insurance - Specialty, Investment - Banking & Investment Services, Shell Companies
Industries in the Healthcare sector are: Biotechnology, Drug Manufacturers - General, Drug Manufacturers - Specialty & Generic, Healthcare, Medical - Care Facilities, Medical - Devices, Medical - Diagnostics & Research, Medical - Distribution, Medical - Equipment & Services, Medical - Healthcare Information Services, Medical - Healthcare Plans, Medical - Instruments & Supplies, Medical - Pharmaceuticals, Medical - Specialties
Industries in the Industrials sector are: Aerospace & Defense, Agricultural - Machinery, Airlines, Airports & Air Services, Business Equipment & Supplies, Conglomerates, Construction, Consulting Services, Electrical Equipment & Parts, Engineering & Construction, Industrial - Distribution, Industrial - Infrastructure Operations, Industrial - Machinery, Industrial - Pollution & Treatment Controls, Industrial - Specialties, Integrated Freight & Logistics, Manufacturing - Metal Fabrication, Manufacturing - Textiles, Manufacturing - Tools & Accessories, Marine Shipping, Railroads, Rental & Leasing Services, Security & Protection Services, Specialty Business Services, Staffing & Employment Services, Trucking, Waste Management
Industries in the Real Estate sector are: REIT - Diversified, REIT - Healthcare Facilities, REIT - Hotel & Motel, REIT - Industrial, REIT - Mortgage, REIT - Office, REIT - Residential, REIT - Retail, REIT - Specialty, Real Estate - Development, Real Estate - Diversified, Real Estate - Services
Industries in the Technology sector are: Communication Equipment, Computer Hardware, Consumer Electronics, Electronic Gaming & Multimedia, Hardware, Equipment & Parts, Information Technology Services, Semiconductors, Software - Application, Software - Infrastructure, Software - Services, Technology Distributors
Industries in the Utilities sector are: Diversified Utilities, Independent Power Producers, Regulated Electric, Regulated Gas, Regulated Water, Renewable Utilities
"""



example_1 = """
# Provide a list of some american companies in financial sector with moderate volatility and high return
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'US'}})
MATCH (stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
MATCH (stock)-[:BELONGS_TO_SECTOR]-> (sector:Sector {{name: 'Financial Services'}})
WHERE attribute.volatility = 'Medium'
  AND (attribute.return = 'High' OR attribute.return = 'Very High')
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
ORDER BY stock.yearly_return DESC, stock.yearly_volatility ASC
LIMIT 30
"""

example_2 = """
# Provide a list of  20 Japanese companies in technology sector with high volatility and low return
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'JP'}})
MATCH (stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
MATCH (stock)-[:BELONGS_TO_SECTOR]-> (sector:Sector {{name: 'Technology'}})
WHERE (attribute.volatility = 'High' OR attribute.volatility = 'Very High')
       AND (attribute.return = 'Low' OR attribute.return = 'Very Low')
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
ORDER BY stock.yearly_return DESC, stock.yearly_volatility ASC
LIMIT 20
"""



example_3 = """
# Select some american technology companies in computer hardware industry with positive yearly return and lowest possible beta
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'US'}})
MATCH (stock)-[:BELONGS_TO_SECTOR]->(sector:Sector {{name: 'Technology'}})
MATCH (stock)-[:BELONGS_TO_INDUSTRY]->(industry:Industry {{name: 'Computer Hardware'}})
WHERE stock.beta IS NOT NULL AND stock.yearly_return > 0
RETURN stock.symbol AS Symbol,
       stock.name AS Name
ORDER BY stock.beta ASC
LIMIT 30
"""

example_4 = """
# Select stocks with very high average trading volume
MATCH (stock:Stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
WHERE (attribute.average_trading_volume = 'High' OR attribute.average_trading_volume = 'Very High')
RETURN stock.symbol AS Symbol,
       stock.name AS Name
LIMIT 30
"""

example_5 = """
# Select stocks with the highest market capitalization
MATCH (stock:Stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
WHERE (attribute.market_capitalization = 'High' OR attribute.market_capitalization = 'Very High')
RETURN stock.symbol AS Symbol,
       stock.name AS Name
ORDER BY stock.market_capitalization_amount DESC
LIMIT 30
"""

example_6 = """
# Select stocks with the highest market capitalization and highest yearly return
MATCH (stock:Stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
WHERE (attribute.market_capitalization = 'High' OR attribute.market_capitalization = 'Very High')
AND (attribute.return = 'High' OR attribute.return = 'Very High')
RETURN stock.symbol AS Symbol,
       stock.name AS Name
ORDER BY stock.market_capitalization_amount DESC
LIMIT 30
"""


example_7 = """
# Provide a list of companies with folowing tickers: AAPL, MSFT, AMZN, GOOGL, FB, TSLA, BRK.A, V, JPM, JNJ
MATCH (stock:Stock)
WHERE stock.symbol IN ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'FB', 'TSLA', 'BRK.A', 'V', 'JPM', 'JNJ', '272210.KS', 'AVAV']
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
"""





example_10 = """
# Provide a list of some american companies with medium volatility and chinese companies in energy sector
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'US'}})
MATCH (stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
MATCH (stock)-[:BELONGS_TO_SECTOR]->(sector:Sector)
WHERE attribute.volatility = 'Medium'
WITH stock, country, attribute
ORDER BY stock.yearly_return DESC, stock.yearly_volatility ASC
LIMIT 10
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
UNION ALL
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'CN'}})
MATCH (stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
MATCH (stock)-[:BELONGS_TO_SECTOR]->(sector:Sector {{name: 'Energy'}})
WITH stock, attribute, country
ORDER BY stock.yearly_return DESC, stock.yearly_volatility ASC
LIMIT 10
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
"""



example_11 = """
# Provide a list of some british and german stocks
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'UK'}})
ORDER BY stock.yearly_return DESC, stock.yearly_volatility ASC
LIMIT 10
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
UNION ALL
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'DE'}})
ORDER BY stock.yearly_return DESC, stock.yearly_volatility ASC
LIMIT 10
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
"""


example_12 = """
#Suggest 10 American stocks with high market capitalization and 10 Chinese stocks with high volatility and 5 German companies with moderate beta

MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'US'}})
MATCH (stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
WHERE attribute.market_capitalization = 'High' OR attribute.market_capitalization = 'Very High'
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
ORDER BY stock.yearly_return DESC
LIMIT 10
UNION ALL
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'CN'}})
MATCH (stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
WHERE (attribute.volatility = 'High' OR attribute.volatility = 'Very High')
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
ORDER BY stock.yearly_return DESC, stock.yearly_volatility ASC
LIMIT 10
UNION ALL
MATCH (stock:Stock)-[:BASED_IN]->(country:Country {{name: 'DE'}})
MATCH (stock)-[:HAS_ATTRIBUTE]->(attribute:Attribute)
WHERE stock.beta > 0.5 AND stock.beta < 1.5
RETURN stock.symbol AS Symbol, 
       stock.name AS Name
ORDER BY stock.yearly_return DESC, stock.yearly_volatility ASC
LIMIT 10
"""