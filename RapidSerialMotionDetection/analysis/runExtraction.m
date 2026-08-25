% -------------------------------------------------------------------------
% RUN EXTRACTION
% -------------------------------------------------------------------------
% This script converts mwk2 files (MWorks) into usable mat files to further
% processe them. Data for performance, impulse sequence, first-order, and
% second-order reverese correlation are derived from processed files.
% Processed data are stored as tables assigned to one data structure for 
% each subject. Alternatively, data for the first order and seconde order
% reverese correlation can be computed by using previously extracted data
% of impulse sequence (use 'extract_from_mw = 0').
% Prior to computing the reverse correlation, trial data is filtered by 
% hit rate performance. The threshold for valid trials is predefined as
% 60% ('HitRate_THRESHOLD').
%
% Version   : 1.0
% Date      : 22/08/2026
% Author    : Maximiian Hohmann
% -------------------------------------------------------------------------



% ----- SETUP -------------------------------------------------------------

clearvars;
close all;
clc;
rng(42);


extract_from_mw = 1;
% determines whether (1) all data are computed based on extraction of the 
% original mwk2 file or (0) data are computed based on preexisting data of 
% impulse sequence


HitRate_THRESHOLD = 0.6
% define the threshold value for filtering out trial data for computing 
% reverse correlations


% set required paths
your_path = ('/Users/mhohmann/Desktop/RSMD');
addpath(fullfile(your_path, 'analysis'));

% for helper functions
addpath('/Users/mhohmann/Desktop/MatLab_MWorks');
addpath(fullfile(your_path, 'analysis','helpers'));
  
mw_dir  = fullfile(your_path, 'data_raw');          % raw data folder
mat_dir = fullfile(your_path, 'data_processed');    % processed data folder

if ~exist(mat_dir, 'dir');  mkdir(mat_dir);   end


motions = {"CW", "CCW", "EXP", "CON"};
session = {"train", "poor", "full"};


% get list of subject folders
subj_folder = dir(mw_dir);
subj_folder = subj_folder([subj_folder.isdir]);         % only directories
subj_folder = subj_folder(~ismember({subj_folder.name}, {'.','..'}));


nSUBJECTS   = length(subj_folder);
nMOTIONS    = numel(motions);
nSESSIONS   = numel(session);



% ----- SELECT SUBJECT FILES ----------------------------------------------

fprintf('\nstart data  converting data files ...\n')


% iteration over subjects
for i = 1:nSUBJECTS
    
    isSubject = string(subj_folder(i).name);
    fprintf('--------------------------------------------------\n')
    fprintf('subject \t: %s\t\t\t(%.f / %.f)\n', isSubject, i, nSUBJECTS)


    % clear data for each subject
    clear data

    % initialize data structure
    data.PERFORMANCE    = table();
    data.SEQUENCE       = table();
    data.RMC_1_mat      = table();
    data.RMC_2_mat      = table();


    % path for mat file (output)
    out_file = isSubject + "_processed.mat";
    out_path = fullfile(mat_dir,  out_file);


        
    % ----- SELECT MOTION FILES -------------------------------------------

    for m = 1:nMOTIONS
        
        isMotion = motions{m};
        fprintf('\tmotion \t: %s\n', isMotion)

        

        % ----- SELECT SESSION FILE ---------------------------------------

        for s = 1:nSESSIONS

            isSession = session{s};
            fprintf('\t\tsession\t: %s\t', isSession)



            % ----- PROCESS DATA ------------------------------------------

            % extract mw file
            if extract_from_mw == 1
            
                % get list of mwk2 files of current subject
                mw_subfolder = dir(fullfile(mw_dir, isSubject, '*.mwk2'));

                file_idx    =  "_" + isMotion + "_" + isSession;
                idx         = contains({mw_subfolder.name}, file_idx);
                
                % check if file exists
                if sum(idx) ~= 1    % one file only
                    fprintf('\t')
                    warning('off','backtrace')
                    warning('Missing File\n\t\t\t\t\t(%s_%s_%s)', ...
                            isSubject, isMotion, isSession)
                    warning('on','backtrace')
                    continue
                end
                
                % path for mw file (input)
                file_path = fullfile(mw_subfolder(idx).folder, ...
                                     mw_subfolder(idx).name);
            
    
                % convert mwk2 file to mat file
                [~, mw_data] = evalc('MW_readFile(file_path, ''include'', {''TRIAL_'', ''IO_'', ''EXP_'', ''LUM_'', ''MOT_'', ''IMP_'', ''RDP_dir''}, ''~cleanTrialBorders'')');
    
                % process mat file
                [PERFORMANCE, SEQUENCE] = processData(mw_data);


                % add ID label
                PERFORMANCE  = addvars(PERFORMANCE, ...
                    repmat(isSubject, size(PERFORMANCE,1), 1), ...
                    'Before', 1, 'NewVariableNames', 'ID');

                SEQUENCE    = addvars(SEQUENCE, ...
                    repmat(isSubject, size(SEQUENCE,1), 1), ...
                    'Before', 1, 'NewVariableNames', 'ID');



            % use pre-existing impulse sequence
            elseif extract_from_mw == 0

                % get list of mat files of current subject
                mat_subfolder = dir(fullfile(mat_dir, '*.mat'));

                file_idx    = isSubject + "_processed";
                idx         = contains({mat_subfolder.name}, file_idx);

                % check if file exists
                if sum(idx) ~= 1    % one file only
                    fprintf('\t')
                    warning('off','backtrace')
                    warning('Missing File\n\t\t\t\t\t(%s_processed)', isSubject)
                    warning('on','backtrace')
                    continue
                end

                % path for mat file (input)
                file_path = fullfile(mat_dir, mat_subfolder(idx).name);

                % load data
                load(file_path);


                % get performance for current condition and motion
                idx = data.PERFORMANCE.Session == isSession & ...
                      data.PERFORMANCE.Motion == isMotion;

                PERFORMANCE = data.PERFORMANCE(idx,:);
            
                % get sequence for current condition and motion
                idx = data.SEQUENCE.Session == isSession & ...
                      data.SEQUENCE.Motion == isMotion;

                SEQUENCE    = data.SEQUENCE(idx,:);
            
                % check if data exists
                if isempty(PERFORMANCE) || isempty(SEQUENCE)
                    fprintf('\t')
                    warning('off','backtrace')
                    warning('Missing Data\n\t\t\t\t\t(%s_%s_%s)', ...
                            isSubject, isMotion, isSession)
                    warning('on','backtrace')
                    continue
                end
            end



            % ----- REVERSE CORRELATION -----------------------------------
            
            % only use trials with adequate lumanance detection
            is_valid_trial = false(size(PERFORMANCE,1), 1);

            % compute luminance hit rate
            nTargets    = cell2mat(PERFORMANCE.LUM_TARGETS);
            nHits       = cell2mat(PERFORMANCE.LUM_HIT);
            HitRate     = nHits ./ nTargets;


            % filter trials by hit rate performance
            is_valid_trial(HitRate >= HitRate_THRESHOLD;
            fprintf('\t\t\t\t\t(%d valid trials)\n', sum(is_valid_trial))


            % compute 1st order motion reverse correlation
            [RMC_1_mat] = getMRC_1(SEQUENCE(is_valid_trial,:));

            % compute 2nd order motion reverse correlation
            [RMC_2_mat] = getMRC_2(SEQUENCE(is_valid_trial,:));


            % add ID, motion, and session label
            RMC_1_mat  = addvars(RMC_1_mat, ...
                    repmat(isSubject, size(RMC_1_mat,1), 1), ...
                    repmat(isMotion, size(RMC_1_mat,1), 1), ...
                    repmat(isSession, size(RMC_1_mat,1), 1), ...
                    'Before', 1, ...
                    'NewVariableNames', {'ID', 'Motion', 'Session'});

            RMC_2_mat  = addvars(RMC_2_mat, ...
                    repmat(isSubject, size(RMC_2_mat,1), 1), ...
                    repmat(isMotion, size(RMC_2_mat,1), 1), ...
                    repmat(isSession, size(RMC_2_mat,1), 1), ...
                    'Before', 1, ...
                    'NewVariableNames', {'ID', 'Motion', 'Session'});



            % ----- AGGREGATE TABLES --------------------------------------
            
            % assign tables to data struct
            data.PERFORMANCE    = [data.PERFORMANCE; PERFORMANCE];
            data.SEQUENCE       = [data.SEQUENCE; SEQUENCE];
            data.RMC_1_mat      = [data.RMC_1_mat; RMC_1_mat];
            data.RMC_2_mat      = [data.RMC_2_mat; RMC_2_mat];
        end
    end


    % save data struct
    save(out_path, 'data');
end


fprintf('--------------------------------------------------\n')
fprintf('successfully converted all data files!\n')

