import concurrent.futures, warnings
from py2neo import Graph, Node, Relationship, NodeMatcher, DatabaseError, RelationshipMatcher
from util import *


class CCFraudPipeline:
    """
    Pipeline entity extracts raw credit card transactions dataset
    ,creates relational graph and loads nodes with relations into database.
    """
    
    # instantiate pipeline
    # load raw credit card dataset and obtain dataframe object from csv file
    # connect to graph database
    def __init__(self, csv_filename: str = "fraudTrain.csv"):
        """
        csv_filename : name of csv file containing dataset within the directory
        """
        try:
            self.__df = pd.read_csv(rf"./{csv_filename}")
            err = self.__connectDB()
            if err.status:
                Log(err)
        except pd.errors.ParserError as e:
            Log(error(detail=str(e)))

    # connect to neo4j database 
    def __connectDB(self) -> error:
        try:
            self.__graph = Graph("neo4j://localhost:7687", auth=("neo4j", "password"))
            self.__matcher = NodeMatcher(self.__graph)
            print("Connected to Graph DB \n")
            return error(status=False, detail="", fatal=False)
        except Exception as e:
            return error(str(e))
        
    
    # create customers dataframe with unique customers and
    # relevant attributes to credit card transaction analysis
    def __makeCustomerDF(self, attr: list) -> pd.DataFrame:
        """
        attr: list of customer attributes relevant to the analysis
        """
        Data = self.__df.copy() # create a copy of the data to work with
        unique_customers = Data.drop_duplicates(subset="cc_num")  # reduce data to entries with unique cc_num
        unique_customers.drop(columns=[col for col in list(Data.columns) if col not in attr],
                       inplace=True)      # drop irrelevant attributes
        if "first" in unique_customers.columns and "last" in unique_customers.columns:
            unique_customers["card_holder"] = unique_customers["first"] + " " + unique_customers["last"]     # merge first and last names to create fullname
            unique_customers.drop(columns=["first", "last"], inplace=True) # drop first and last for name
        print("Created Customer Dataframe \n")
        return unique_customers
    
    
    # create merchants dataframe with unique merchants and
    # relevant attributes to credit card transaction analysis
    def __makeMerchantDF(self, attr: list) -> pd.DataFrame:
        """
        attr: list of merchant attributes relevant to the analysis
        """
        Data = self.__df.copy() # create a copy of the data to work with
        unique_merchants = Data.drop_duplicates(subset="merchant")  # reduce data to entries with unique merchant
        unique_merchants.drop(columns=[col for col in list(Data.columns) if col not in attr],
                       inplace=True)      # drop irrelevant attributes
        print("Created Merchant Dataframe \n")
        return unique_merchants
    

    # create purchase dataframe with unique purchase transactions and
    # relevant attributes to credit card transaction analysis
    def __makeTransactionDF(self, attr: list) -> pd.DataFrame:
        """
        attr: list of transaction attributes relevant to the analysis
        """
        Data = self.__df.copy() # create a copy of the data to work with
        unique_purchases = Data.drop_duplicates(subset="trans_num") # reduce data to entries with unique transaction numbers
        unique_purchases.drop(columns=[col for col in list(Data.columns) if col not in attr],
                       inplace=True)      # drop irrelevant attributes
        if "trans_date" in unique_purchases.columns:
            unique_purchases["trans_date"] = unique_purchases["trans_date"].apply(convert_to_neo4j_date) # modify transaction date format
        print("Created Purchase Transaction Dataframe \n")
        return unique_purchases
    
    #  Load Dataframe records as nodes into GraphDB
    def loadNodeFromDF(self, df: pd.DataFrame, label: str, primaryKey: str):
        """
        df : dataframe to be loaded into neo4j as category with records as nodes
        label: name for category in neo4j database
        primaryKey : unique constraint is applied to named property on node 
        to avoid duplicate nodes being created for the same value of named property.
        """
        print(f"Now loading nodes into {label} Category \n")
        for _, row in df.iterrows():
            # Create node
            properties = {}
            for column in df.columns:
                properties[column] = row[column]
            node = Node(label, **properties)
            # Merge node in the graph
            self.__graph.merge(node, label, primaryKey)
        
        print(f"Done loading nodes into {label} Category \n")

    
    # Load customer and merchant nodes into GraphDB
    def loadCustomerMerchant(self, attrDict: dict = {
        "customer" : [], # list of customer attributes
        "merchant" : [] # list of merchant attributes
    }):
        """
        attrDict: dictionary mapping of attributes relevant to each entity category
        """
        try:
            print("Checking if nodes labels already exist in database...\n")
            labels = ["Customer", "Merchant"]
            nodes_exist = all(self.__matcher.match(label).first() for label in labels)
            if nodes_exist:
                # If nodes exist, delete them along with their relationships
                proceed = input("Do you want to overhaul existing nodes? (Yes/No) ")
                if proceed in ["No", "no", "N", "n"]:
                    return
                elif proceed in ["Yes", "y", "Y", "yes"]:
                    for label in labels:
                        nodes_to_delete = list(self.__matcher.match(label))
                        for node in nodes_to_delete:
                            self.__graph.delete(node)
                    print("Nodes and relationships with labels {} deleted successfully.".format(labels))
                else:
                    self.loadCustomerMerchant(attrDict)
            else:
                print("Nodes with labels {} do not exist in the database.".format(labels))
            customerDF = self.__makeCustomerDF(attrDict.get("customer", list(self.__df.columns))) 
            merchantDF = self.__makeMerchantDF(attrDict.get("merchant", list(self.__df.columns)))
            
            print("Ready to Load Nodes into GraphDB \n")
            # Create nodes concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit the node creation tasks
                futures = [
                executor.submit(self.loadNodeFromDF, item.df, item.label, item.key)
            for item in [dfNode(customerDF, "Customer", "cc_num"),
                    dfNode(merchantDF, "Merchant", "merchant")]]
                for _ in concurrent.futures.as_completed(futures):
                    pass
            print("Done Loading all Nodes into GraphDB \n")
        except Exception as e:
             Log(error(detail= str(e)))


    # Establish a relationship between customer node and merchant node based on purchase (transaction)
    def createCustomerMerchantRelation(self, relation_type: str):
        """
        relation_type : Name describing type of relationship between the nodes
        """
        try:
            print("Checking for existing relationships between Customer and Merchant Nodes... \n")

             # Query to check if the relationship type exists between the two labels
            query = f"MATCH (:Customer)-[:`{relation_type}`]->(:Merchant) RETURN COUNT(*)"
            # Execute the query and check the result
            result = self.__graph.run(query).evaluate()
            
            if result > 0:
                proceed = input("Do you want to overhaul existing relationships? (Yes/No) ")
                if proceed in ["Yes", "y", "Y", "yes"]:
                    query = (
                        f"MATCH (c:Customer)-[r]-(m:Merchant)"
                        "DELETE r"
                                )
                    self.__graph.run(query)
                    print(f"All existing relationships between Customer and Merchant nodes have been deleted. \n")
                elif proceed in  ["No", "no", "N", "n"]:
                    pass
                else:
                    self.createCustomerMerchantRelation()
            else:
                try:
                    query = f"CREATE CONSTRAINT FOR ()-[r:{relation_type}]-() REQUIRE r.trans_num IS UNIQUE;"
                    self.__graph.run(query)
                    print("Constraint created on relationship {} for uniqueness of transaction number (trans_num)".format(relation_type))
                except:
                    pass

            purchaseDF = self.__makeTransactionDF(["cc_num", "merchant",
            "trans_date", "trans_time", "trans_num","amt","unix_time"])
            
            # get purchases dataframe in batches of size 10 000
            def getPuchaseBatches():
                batches = []
                for i in range(0, len(purchaseDF), 10000):
                    batch = purchaseDF.iloc[i:i+10000]
                    batches.append(batch)
                print("Purchase batches acquired...\n")
                return batches


            # create relationship between existing customer and merchant nodes based on purchase batch dataframes
            def createRelation(subsetDF: pd.DataFrame):
                """
                subsetDF : subset of purchase dataframe (batch )
                """
                print(f"Ready to create relationship between Customer and Merchant from \
                      transaction_number {subsetDF['trans_num'].iloc[0]} \
                        to transaction_number {subsetDF['trans_num'].iloc[-1]} \n")
                for _, row in subsetDF.iterrows():
                    # Match existing customer and merchant nodes
                    customer = self.__graph.nodes.match('Customer', cc_num=row['cc_num']).first()
                    merchant = self.__graph.nodes.match('Merchant', merchant=row['merchant']).first()
                    # Create the relationship
                    try:
                        relationship = Relationship(customer, relation_type, 
                            merchant, amount=float(row['amt']), date=row["trans_date"], trans_num=row["trans_num"],
                            time=row["trans_time"], timestamp=row["unix_time"])
                        # Create the relationship in the graph
                        self.__graph.create(relationship)
                    except:
                        continue
                
                print(f"Done Establishing relationship between Customer and Merchant \
              from transaction_nummber {subsetDF['trans_num'].iloc[0]} to \
                transaction_number {subsetDF['trans_num'].iloc[-1]} \n")

            print("Starting Relationship creation between Customer and Merchant Nodes in GraphDB... \n")
            # Create relationships concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit the relationship creation tasks
                futures = [executor.submit(createRelation, data) for data in getPuchaseBatches()]
                for _ in concurrent.futures.as_completed(futures):
                    pass
            print("Done creating all relationship between Customer and Merchant based on \
                  all purchase transactions history. \n")
        except Exception as e:
            Log(error(detail= str(e)))

if __name__ == "__main__":

    warnings.filterwarnings("ignore")

    setup_logging() # set logging configuration

    pipe = CCFraudPipeline() # intialize pipeline with dataset 

    pipe.loadCustomerMerchant({
        "customer" : [ "first", "last", "cc_num", "gender", "zip", "state", "job", "city"],
        "merchant": ["merchant", "category"]
    }) # load customer and merchant nodes into DB

    pipe.createCustomerMerchantRelation("MADE_PURCHASE_AT") # establish customer merchant relations based on transaction history
    
        