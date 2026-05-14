from src.common.database import Base, engine


def main():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
