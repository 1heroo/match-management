import pandas as pd


class XlsxUtils:
    def handle_xlsx(self, df: pd.DataFrame, file_name) -> pd.DataFrame:
        index = self.search_table_begin(df=df)
        df = df.loc[index:]
        df.to_csv(file_name)

        self.delete_first_line(filename=file_name)
        df = pd.read_csv(file_name)
        for column in df:
            if 'Unnamed' in column:
                df = df.drop(column, axis=1)
        return df

    @staticmethod
    def search_table_begin(df: pd.DataFrame):
        article_columns = ['артикул', "Артикул", "артикулы", "Артикулы"]
        columns = df.columns
        for index in df.index[:100]:
            for column in columns:
                if df[column][index] in article_columns or column in article_columns:
                    return index

    @staticmethod
    def delete_first_line(filename):
        with open(filename, "r", encoding='utf-8') as fp:
            lines = fp.readlines()

        with open(filename, "w", encoding='utf-8') as fp:
            for line in range(1, len(lines)):
                fp.write(lines[line])

    @staticmethod
    def find_article_column(df: pd.DataFrame):
        columns = df.columns

        article_list = ['артикул', "Артикул", "Артикулы", "артикулы"]
        for column in columns:
            if column in article_list:
                return column

    @staticmethod
    def find_price_column(df: pd.DataFrame):
        columns = df.columns

        price_list = ["РРЦ", "МДЦ", 'МРЦ', "РРЦ Цена", "МДЦ АКЦИЯ!", 'Цена РРЦ', 'РРЦ Wildberries, руб']
        for column in columns:
            if column in price_list:
                return column
