import logging
import pickle
import csv

import GPy
import numpy as np

from savigp import SAVIGP
from savigp_diag import SAVIGP_Diag
from savigp_single_comp import SAVIGP_SingleComponent
from optimizer import Optimizer
from util import id_generator, check_dir_exists, get_git


class ModelLearn:
    @staticmethod
    def get_output_path():
        """
        :return: the path in which results of the experiment will be saved
        """
        return '../results/'

    @staticmethod
    def get_logger_path():
        """
        :return: the path in which log files will be created
        """
        return '../logs/'

    @staticmethod
    def get_logger(name, level):
        """
        Creates loggers
        :param name: name of the log file
        :param level: level of debugging
        :return: created loggers
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        check_dir_exists(ModelLearn.get_logger_path())
        fh = logging.FileHandler(ModelLearn.get_logger_path() + name + '.log')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    @staticmethod
    def export_train(name, Xtrain, Ytrain, export_X=False):
        """
        Exports training data into a csv file
        :param name: name of file
        :param Xtrain: 'X' of training data
        :param Ytrain: 'Y' of training data
        :param export_X: whether to export 'X'. If False, only Ytrain will be exported
        :return:
        """
        path = ModelLearn.get_output_path() + name + '/'
        check_dir_exists(path)
        file_name = 'train_'
        header =['Y%d,' % (j) for j in range(Ytrain.shape[1])]
        data= None
        if export_X:
            data = np.hstack((Ytrain, Xtrain))
            header += ['X%d,' % (j) for j in range(Xtrain.shape[1])]
        else:
            data = Ytrain
        np.savetxt(path + file_name + '.csv', data , header=''.join(header), delimiter=',', comments='')


    @staticmethod
    def export_track(name, track):
        """
        exports trajectory of the objective function
        :param name: name of the file
        :param track: trajectory of the objective function
        :return: None
        """
        path = ModelLearn.get_output_path() + name + '/'
        check_dir_exists(path)
        file_name = 'obj_track_'
        np.savetxt(path + file_name + '.csv', np.array([track]).T,
                   header='objective'
                   , delimiter=',', comments='')

    @staticmethod
    def export_model(model, name):
        """
        exports Modle into a csv file
        :param model: the model to be exported
        :param name: name of the csv file
        :return: None
        """
        path = ModelLearn.get_output_path() + name + '/'
        check_dir_exists(path)
        file_name = 'model_'
        if model is not None:
            with open(path + file_name + '.csv', 'w') as fp:
                f = csv.writer(fp, delimiter=',')
                f.writerow(['#model', model.__class__])
                params = model.get_all_params()
                param_names = model.get_all_param_names()
                for j in range(len(params)):
                    f.writerow([param_names[j], params[j]])


    @staticmethod
    def export_test(name, X, Ytrue, Ypred, Yvar_pred, nlpd, pred_names, export_X=False):
        """
        Exports test data and the predictions into a csv file
        :param name: name of the file
        :param X: 'X' for which prediction have been made
        :param Ytrue: The true values of 'Y'
        :param Ypred: Predictions
        :param Yvar_pred: Variance of the prediction
        :param nlpd: NLPD of the predictions
        :param pred_names:
        :param export_X: Whether to export 'X' to the csv file. If False, 'X' will not be exported into the csv file.
        :return: None
        """
        path = ModelLearn.get_output_path() + name + '/'
        check_dir_exists(path)
        file_name = 'test_'
        out = []
        out.append(Ytrue)
        out += Ypred
        out += Yvar_pred
        out += [nlpd]
        header =  ['Ytrue%d,' % (j) for j in range(Ytrue.shape[1])] + \
            ['Ypred_%s_%d,' % (m, j) for m in pred_names for j in range(Ypred[0].shape[1])] + \
            ['Yvar_pred_%s_%d,' % (m, j) for m in pred_names for j in range(Yvar_pred[0].shape[1])] + \
            ['nlpd,'] + ['NLPD_%d,' % (j) for j in range(nlpd.shape[1]-1)]


        if export_X:
            out.append(X)
            header += ['X%d,' % (j) for j in range(X.shape[1])]

        header = ''.join(header)
        out = np.hstack(out)
        np.savetxt(path + file_name + '.csv', out
                   , header=header
                   , delimiter=',', comments='')


    @staticmethod
    def export_configuration(name, config):
        """
        Exports configuration of the model as well as optimize to a csv file
        :param name: Name of the file
        :param config: Configuration to be exported
        :return: None
        """
        path = ModelLearn.get_output_path() + name + '/'
        check_dir_exists(path)
        file_name = path + 'config_' + '.csv'
        with open(file_name, 'wb') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=config.keys())
            writer.writeheader()
            writer.writerow(config)

    @staticmethod
    def get_ID():
        """
        :return: A random ID
        """
        return id_generator(size=6)


    @staticmethod
    def opt_callback(name):
        def callback(model, current_iter, total_evals, delta_m, delta_s, obj_track):
            path = ModelLearn.get_output_path() + name + '/'
            check_dir_exists(path)
            pickle.dump(model.image(), open(path + 'model.dump', 'w'))
            pickle.dump({
                'current_iter': current_iter,
                'total_evals': total_evals,
                'delta_m': delta_m,
                'delta_s': delta_s,
                'obj_track': obj_track,
                'obj_fun': model.objective_function()
            },
                        open(path + 'opt.dump', 'w'))
        return callback


    @staticmethod
    def run_model(Xtest, Xtrain, Ytest, Ytrain, cond_ll, kernel, method, name, run_id, num_inducing, num_samples,
                  sparsify_factor, to_optimize, trans_class, random_Z, logging_level, export_X,
                  latent_noise=0.001, opt_per_iter=None, max_iter=200, n_threads=1, model_image_file=None,
                  xtol=1e-3, ftol=1e-5, partition_size=3000):
        """
        Fits a model to the data (Xtrin, Ytraing) using the method provided by 'method', and makes predictions on
         'Xtrest' and 'Ytest', and exports the result to several csv files.
        :param Xtest: X of test points
        :param Xtrain: X of training points
        :param Ytest: Y of test points
        :param Ytrain: Y of traiing points
        :param cond_ll: Conditional log likelihood function used to build the model. It should be subclass of
        likelihood/Likelihood
        :param kernel: The kernel that the model uses. It should be an array, and size of the array should be same as the
         number of latent processes
        :param method: The method to use to learns the model. It can be 'full', 'mix1', and 'mix2'
        :param name: The name that will be used for logger file names, and results files names
        :param run_id: ID of the experiment, which can be anything, and it will be included in the configuation file
        :param num_inducing: Number of inducing points
        :param num_samples: Number of samples for estimating objective function and gradients
        :param sparsify_factor: Can be any number and will be included in the configuration file. It will not determine
        the number of inducing points
        :param to_optimize: The subject of parameters to optimize. It should be a list, and it can include 'll', 'mog', 'hyp', e.g.,
        it can be ['ll', 'mog']
        :param trans_class: The class which will be used to transform data.
        :param random_Z: Whether to initialise inducing points randomly on the training data. If False, inducing points
        will be placed using k-means clustering. If True, inducing points will be placed randomly on the training data.
        :param logging_level: The logging level to use.
        :param export_X: Whether to export X to csv files.
        :param latent_noise: The amount of latent noise to add to the kernel. A white noise of amount latent_noise will be
        added to the kernel.
        :param opt_per_iter: Number of update of each subset of parameters in each iteration, e.g., {'mog': 15000, 'hyp': 25, 'll': 25}
        :param max_iter: Maximum of global iterations used on optimization.
        :param n_threads: Maximum number of threads used.
        :param model_image_file: The image file from the which the model will be initialized.
        :param xtol: Tolerance of 'X' below which the optimization is determined as converged.
        :param ftol: Tolerance of 'f' below which the optimization is determined as converged.
        :param partition_size: The size which is used to partition training data. This is not the partition used for SGD.
        Training data will be split to the partitions of size 'partition_size' and calculations will be done on each paritions
        separately.
        :return: a tuple, where the first element is the name of the folder in which results are stored, and the
        second element is the model itself.
        """

        if opt_per_iter is None:
            opt_per_iter = {'mog': 40, 'hyp': 40, 'll': 40}
        folder_name = name + '_' + ModelLearn.get_ID()
        logger = ModelLearn.get_logger(folder_name, logging_level)
        transformer = trans_class.get_transformation(Ytrain, Xtrain)
        Ytrain = transformer.transform_Y(Ytrain)
        Ytest = transformer.transform_Y(Ytest)
        Xtrain = transformer.transform_X(Xtrain)
        Xtest = transformer.transform_X(Xtest)

        opt_max_fun_evals = None
        total_time = None
        timer_per_iter = None
        tracker = None
        export_model = False
        git_hash, git_branch = get_git()

        properties = {'method': method,
                   'sparsify_factor': sparsify_factor,
                   'sample_num': num_samples,
                   'll': cond_ll.__class__.__name__,
                   'opt_max_evals': opt_max_fun_evals,
                   'opt_per_iter': opt_per_iter,
                   'xtol': xtol,
                   'ftol': ftol,
                   'run_id': run_id,
                   'experiment': name,
                   'max_iter': max_iter,
                   'git_hash': git_hash,
                   'git_branch': git_branch,
                   'random_Z': random_Z,
                   'latent_noise:': latent_noise,
                   'model_init': model_image_file
                   }
        logger.info('experiment started for:' + str(properties))

        model_image = None
        current_iter = None
        if model_image_file is not None:
            model_image = pickle.load(open(model_image_file + 'model.dump'))
            opt_params = pickle.load(open(model_image_file + 'opt.dump'))
            current_iter = opt_params['current_iter']

        if model_image:
            logger.info('loaded model - iteration started from: ' + str(opt_params['current_iter']) +
                        ' Obj fun: ' + str(opt_params['obj_fun']) + ' fun evals: ' + str(opt_params['total_evals']))
        if method == 'full':
            m = SAVIGP_SingleComponent(Xtrain, Ytrain, num_inducing, cond_ll,
                                       kernel, num_samples, None, latent_noise, False, random_Z, n_threads=n_threads, image=model_image, partition_size=partition_size)
            _, timer_per_iter, total_time, tracker, total_evals = \
                Optimizer.optimize_model(m, opt_max_fun_evals, logger, to_optimize, xtol, opt_per_iter, max_iter, ftol, ModelLearn.opt_callback(folder_name), current_iter)
        if method == 'mix1':
            m = SAVIGP_Diag(Xtrain, Ytrain, num_inducing, 1, cond_ll,
                            kernel, num_samples, None, latent_noise, False, random_Z, n_threads=n_threads, image=model_image, partition_size=partition_size)
            _, timer_per_iter, total_time, tracker, total_evals = \
                Optimizer.optimize_model(m, opt_max_fun_evals, logger, to_optimize, xtol, opt_per_iter, max_iter, ftol, ModelLearn.opt_callback(folder_name), current_iter)
        if method == 'mix2':
            m = SAVIGP_Diag(Xtrain, Ytrain, num_inducing, 2, cond_ll,
                            kernel, num_samples, None, latent_noise, False, random_Z, n_threads=n_threads, image=model_image, partition_size=partition_size)
            _, timer_per_iter, total_time, tracker, total_evals = \
                Optimizer.optimize_model(m, opt_max_fun_evals, logger, to_optimize, xtol, opt_per_iter, max_iter, ftol, ModelLearn.opt_callback(folder_name), current_iter)
        if method == 'gp':
            m = GPy.models.GPRegression(Xtrain, Ytrain, kernel[0])
            if 'll' in to_optimize and 'hyp' in to_optimize:
                m.optimize('bfgs')

        y_pred, var_pred, nlpd = m.predict(Xtest, Ytest)
        if not (tracker is None):
            ModelLearn.export_track(folder_name, tracker)
        ModelLearn.export_train(folder_name, transformer.untransform_X(Xtrain), transformer.untransform_Y(Ytrain), export_X)
        ModelLearn.export_test(folder_name,
                                transformer.untransform_X(Xtest),
                                transformer.untransform_Y(Ytest),
                                [transformer.untransform_Y(y_pred)],
                                [transformer.untransform_Y_var(var_pred)],
                                transformer.untransform_NLPD(nlpd),
                                [''], export_X)

        if export_model and isinstance(m, SAVIGP):
            ModelLearn.export_model(m, folder_name)

        properties['total_time'] = total_time
        properties['time_per_iter'] = timer_per_iter
        properties['total_evals'] = total_evals
        ModelLearn.export_configuration(folder_name, properties)
        return folder_name, m
