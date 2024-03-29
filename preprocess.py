#  Following https://www.kaggle.com/startupsci/titanic-data-science-solutions

# data analysis and wrangling
import pandas as pd
import numpy as np
import random as rnd


def main():
    train_df = pd.read_csv('./data/train.csv')
    test_df = pd.read_csv('./data/test.csv')
    combine = [train_df, test_df]

    # Remove 'Ticket', 'Cabin' feature
    train_df = train_df.drop(['Ticket', 'Cabin'], axis=1)
    test_df = test_df.drop(['Ticket', 'Cabin'], axis=1)
    combine = [train_df, test_df]

    # Create 'Title' feature
    # Create 'Title' feature
    for dataset in combine:
        dataset['Title'] = dataset.Name.str.extract(' ([A-Za-z]+)\.', expand=False)

    # Replace and group some title
    for dataset in combine:
        dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess', 'Capt', 'Col',
                                                     'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
        dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')

    # Map title into value
    title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}
    for dataset in combine:
        dataset['Title'] = dataset['Title'].map(title_mapping)
        dataset['Title'] = dataset['Title'].fillna(0)

    # Remove 'Name' from dataset
    train_df = train_df.drop(['Name', 'PassengerId'], axis=1)
    test_df = test_df.drop(['Name'], axis=1)
    combine = [train_df, test_df]

    # Map gender into value
    for dataset in combine:
        dataset['Sex'] = dataset['Sex'].map({'female': 1, 'male': 0}).astype(int)

    # Fill the missing value by using median of age for those Pclass and Gender combined
    guess_ages = np.zeros((2, 3))
    # Convert age data as int (rounding to 0.5)

    # Fill Nan with median
    for dataset in combine:
        for i in range(0, 2):
            for j in range(0, 3):
                guess_df = dataset[(dataset['Sex'] == i) & \
                                   (dataset['Pclass'] == j + 1)]['Age'].dropna()

                # age_mean = guess_df.mean()
                # age_std = guess_df.std()
                # age_guess = rnd.uniform(age_mean - age_std, age_mean + age_std)

                age_guess = guess_df.median()

                # Convert random age float to nearest .5 age
                guess_ages[i, j] = int(age_guess / 0.5 + 0.5) * 0.5

        for i in range(0, 2):
            for j in range(0, 3):
                dataset.loc[(dataset.Age.isnull()) & (dataset.Sex == i) & (dataset.Pclass == j + 1), \
                            'Age'] = guess_ages[i, j]

        dataset['Age'] = dataset['Age'].astype(int)

    # Create 'AgeBand' type
    train_df['AgeBand'] = pd.cut(train_df['Age'], 5)

    # Map 'Age' within 'AgeBand'
    for dataset in combine:
        dataset.loc[dataset['Age'] <= 16, 'Age'] = 0
        dataset.loc[(dataset['Age'] > 16) & (dataset['Age'] <= 32), 'Age'] = 1
        dataset.loc[(dataset['Age'] > 32) & (dataset['Age'] <= 48), 'Age'] = 2
        dataset.loc[(dataset['Age'] > 48) & (dataset['Age'] <= 64), 'Age'] = 3
        dataset.loc[dataset['Age'] > 64, 'Age'] = 4
    train_df = train_df.drop(['AgeBand'], axis=1)
    combine = [train_df, test_df]

    # Create new features by combining existing feature
    for dataset in combine:
        dataset['FamilySize'] = dataset['SibSp'] + dataset['Parch'] + 1
    # Create feature is alone
    for dataset in combine:
        dataset['IsAlone'] = 0
        dataset.loc[dataset['FamilySize'] == 1, 'IsAlone'] = 1
    train_df = train_df.drop(['Parch', 'SibSp', 'FamilySize'], axis=1)
    test_df = test_df.drop(['Parch', 'SibSp', 'FamilySize'], axis=1)
    combine = [train_df, test_df]

    # Create artificial of Pclass and age
    for dataset in combine:
        dataset['Age*Class'] = dataset.Age * dataset.Pclass

    # Convert embark feature, fill missing data with most common occurance
    freq_port = train_df.Embarked.dropna().mode()[0]
    for dataset in combine:
        dataset['Embarked'] = dataset['Embarked'].fillna(freq_port)

    # Map 'Embarked' into value
    for dataset in combine:
        dataset['Embarked'] = dataset['Embarked'].map({'S': 0, 'C': 1, 'Q': 2}).astype(int)

    # Fill missing value of 'Fare' with training median
    train_df['Fare'].fillna(train_df['Fare'].dropna().median(), inplace=True)
    test_df['Fare'].fillna(train_df['Fare'].dropna().median(), inplace=True)
    # Split by quatile
    train_df['FareBand'] = pd.qcut(train_df['Fare'], 4)
    # Map 'Fare' into value
    for dataset in combine:
        dataset.loc[dataset['Fare'] <= 7.91, 'Fare'] = 0
        dataset.loc[(dataset['Fare'] > 7.91) & (dataset['Fare'] <= 14.454), 'Fare'] = 1
        dataset.loc[(dataset['Fare'] > 14.454) & (dataset['Fare'] <= 31), 'Fare'] = 2
        dataset.loc[dataset['Fare'] > 31, 'Fare'] = 3
        dataset['Fare'] = dataset['Fare'].astype(int)

    train_df = train_df.drop(['FareBand'], axis=1)
    combine = [train_df, test_df]

    X_train = train_df.drop("Survived", axis=1)
    Y_train = train_df["Survived"]
    test_id = test_df["PassengerId"]
    X_test = test_df.drop("PassengerId", axis=1).copy()
    return X_train.to_numpy(), Y_train.to_numpy(), X_test.to_numpy(), test_id.to_numpy()


if __name__ == "__main__":
    X_train, Y_train, X_test, id = main()
    print(Y_train)