% -------------------------------------------------------------------------
% FIT TUNING CURVES
% -------------------------------------------------------------------------
% This script generates correlograms based on probability values from the
% reversed motion correlation for each motion direction (CW, CCW, EXP, CON)
% and each attention condition (high, low). Tuning curve is then derived
% from probabilities at the latency to the response onset at which the 
% propability value are the highest.
%
%
% Version   : 1.0
% Date      : 29/06/2026
% Author    : Maximiian Hohmann
% -------------------------------------------------------------------------



% ----- SETUP -------------------------------------------------------------

clearvars;
close all;
clc;
rng(42);


% set required paths
your_path = ('/Users/mhohmann/Desktop/RSVMP');
addpath(fullfile(your_path, 'analysis'));

% for helper functions
addpath(fullfile(your_path, 'analysis','helpers'));


% data folder
data_dir    = fullfile(your_path, 'data_processed');
data_folder = dir(fullfile(data_dir, '*.mat'));     % list of data files

% output folder
fig_dir     = fullfile(your_path, 'figures');       % figures
if ~exist(fig_dir, 'dir');  mkdir(fig_dir); end

params_dir  = fullfile(your_path, 'params');        % fitting params    
if ~exist(params_dir, 'dir');   mkdir(params_dir);  end



motionType  = {"CW", "CCW", "CW_CCW", "EXP", "CON", "EXP_CON"};





% get list of subject IDs
IDs = string(erase({data_folder.name}, '_processed.mat'));


% exclude subjects
% pattern = {'AhF', 'AkE'};
% IDs = IDs(~ismember(IDs, pattern));


nSUBJECTS   = length(data_folder);
nMOTIONS    = numel(motionType);




%% ----- INDIVIDUAL TUNING CURVES -----------------------------------------

fprintf('\n fit tuning curves  ...\n')
fprintf('--------------------------------------------------\n')

% initialize cell array
corr_cell = cell(nSUBJECTS,1);
sec_corr_cell = cell(nSUBJECTS,1);



% ----- SELECT SUBJECT FILES ----------------------------------------------

% iteration over subjects
for i = 2:nSUBJECTS

    isSubject = string(data_folder(i).name(1:3));
    fprintf('--------------------------------------------------\n')
    fprintf('subject \t: %s\t\t\t(%.f / %.f)\n', isSubject, i, nSUBJECTS)


    % get correlation values from mat file
    file_path = fullfile(data_dir, data_folder(i).name);
    load(file_path);	% load data

    RMC_1_mat   = data.RMC_1_mat;   % (1st order) correlation values 
    RMC_2_mat   = data.RMC_2_mat;   % (2nd order) correlation values


    % exclude values of training session
    RMC_1_mat(RMC_1_mat.Session == "train",:) = [];
    RMC_2_mat(RMC_2_mat.Session == "train",:) = [];



    % ----- SELECT MOTION TYPE --------------------------------------------

    for m = 1:nMOTIONS

        isMotion = motionType{m}; % current motion type
        fprintf('\tmotion: %s\n', isMotion)


        % define output folder
        output_fig = fullfile(fig_dir, isMotion);
        if ~exist(output_fig, 'dir'); mkdir(output_fig); end

        output_params = fullfile(params_dir, isMotion);
        if ~exist(output_params, 'dir'); mkdir(output_params); end



        % ----- CORRELOGRAM -----------------------------------------------
        
        fig = plotCorrelogram(RMC_1_mat, isMotion, 'SubjectID', isSubject);
        
        % save fig
        filename = fullfile(output_fig, isSubject + "_" + isMotion + "_correlogram.pdf");
        exportgraphics(fig, filename, 'ContentType', 'vector');
        


        % ----- TUNING CURVE ----------------------------------------------

        % % use corr_table to fit a two-Gaussian fuction
        % [fit, res] = computeTuningCurve(corr_table, isMotion);
        % 
        % % save fit params
        % filename = fullfile(output_params, isSubject + "_" + isMotion + "_fit.csv");
        % writetable(fit.params, filename);
        % 
        % % save GoF params
        % filename = fullfile(output_params, isSubject + "_" + isMotion + "_GoF.csv");
        % writetable(fit.GoF, filename);
        % 
        % 
        % % parse res to plotting function
        % fig = plotTuningCurve(res, isMotion, 'SubjectID', isSubject);
        % 
        % % save fig
        % filename = fullfile(output_fig, isSubject + "_" + isMotion + "_tuning_curve.pdf");
        % exportgraphics(fig, filename, 'ContentType', 'vector');



        % ----- HEATMAP ----------------------------------------------

        % fig = plotSecondOrderHeatmap(sec_corr_table, isMotion, 'SubjectID', isSubject);
        % 
        % % save fig
        % filename = fullfile(output_fig, isSubject + "_" + isMotion + "_heatmap.pdf");
        % exportgraphics(fig, filename, 'ContentType', 'vector');


    end

    % store correlation table
    % corr_cell{i} = corr_table;
    % sec_corr_cell{i} = sec_corr_table;

    clear 'data' 'corr_table' sec_corr_table
end

% concatenate once
corr_table = vertcat(corr_cell{:});
sec_corr_table = vertcat(sec_corr_cell{:});



%% ----- AVERAGED TUNING CURVES -------------------------------------------


fprintf('--------------------------------------------------\n')
fprintf('across all subjects:\n')

% iteration over motion types
for m = 2:numel(motionType)

    isMotion = motionType{m}; % current motion type
    fprintf('\tmotion: %s\n', isMotion)

    % define output folder
    output_fig = fullfile(fig_dir, "average", isMotion);
    if ~exist(output_fig, 'dir'); mkdir(output_fig); end

    output_params = fullfile(params_dir, "average", isMotion);
    if ~exist(output_params, 'dir'); mkdir(output_params); end

   
    %% correlogram

    fig = plotCorrelogram(corr_table, isMotion);
    
    % save fig
    filename = fullfile(output_fig, "average_" + isMotion + "_correlogram.pdf");
    exportgraphics(fig, filename, 'ContentType', 'vector');


    %% tuning curve

    % use corr_table to fit a two-Gaussian fuction
    [fit, res] = computeTuningCurve(corr_table, isMotion);
    
    % save fit params
    filename = fullfile(output_params, "average_" + isMotion + "_fit.csv");
    writetable(fit.params, filename);

    % save GoF params
    filename = fullfile(output_params, "average_" + isMotion + "_GoF.csv");
    writetable(fit.GoF, filename);

    
    % parse res to plotting function
    fig = plotTuningCurve(res, isMotion);
    
    % save fig
    filename = fullfile(output_fig, "average_" + isMotion + "_tuning_curve.pdf");
    exportgraphics(fig, filename, 'ContentType', 'vector');


    %% second-order heatmap
    fig = plotSecondOrderHeatmap(sec_corr_table, isMotion);

    % save fig
    filename = fullfile(output_fig, "average_" + isMotion + "_heatmap.pdf");
    exportgraphics(fig, filename, 'ContentType', 'vector');
end

fprintf('--------------------------------------------------\n')
fprintf('--------------------------------------------------\n')
fprintf('completed analysis!\n')

