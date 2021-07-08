from models import Experiment, Filter, MapModel


if __name__ == "__main__":
    # Experiment with feature comparison
    exp_1 = Experiment(maps=[MapModel.CubeTown], filter=Filter.compare_feature, name="A Filter Feature")
    exp_1.run()

    # Experiment with distance comparison
    exp_2 = Experiment(maps=[MapModel.CubeTown], filter=Filter.compare_distance, name="A Distance Filter")
    exp_2.run()
